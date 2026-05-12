import base64
import csv
import io

from odoo import api, fields, models, _

TAX_SINGAPORE_NAMES = ['Sales Tax 9% SR', '[old] Sales Tax 9% SR']
TAX_SINGAPORE_LABEL = '9% SR'
TAX_INTERNATIONAL_NAMES = ['Sales Tax 0% ZR']
TAX_INTERNATIONAL_LABEL = '0% ZR'
SINGAPORE_COUNTRY_CODE = 'SG'

# Price-inclusive taxes: changing these to 0% ZR does NOT change the invoice total,
# so paid invoices can be safely fixed without breaking payment reconciliation.
PRICE_INCLUSIVE_TAX_NAMES = ['[old] Sales Tax 9% SR']


class FixEcomInvoiceTaxWizard(models.TransientModel):
    _name = 'fix.ecom.invoice.tax.wizard'
    _description = 'Fix ECOM Invoice GST Tax Codes'

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    include_posted = fields.Boolean(
        string='Include Confirmed Invoices',
        default=True,
    )
    include_paid = fields.Boolean(
        string='Include Paid / In-Payment Invoices',
        default=True,
        help='Safe to enable when the current tax is price-inclusive ([old] Sales Tax 9% SR). '
             'The invoice total stays the same so payment reconciliation is not broken.',
    )
    invoice_count = fields.Integer(compute='_compute_preview')
    line_count = fields.Integer(compute='_compute_preview')
    skipped_count = fields.Integer(compute='_compute_preview')

    @api.depends('date_from', 'date_to', 'include_posted', 'include_paid')
    def _compute_preview(self):
        for wiz in self:
            fixable, skipped = wiz._get_invoices()
            wiz.invoice_count = len(fixable)
            wiz.line_count = sum(
                len(inv.invoice_line_ids.filtered(lambda l: l.display_type == 'product'))
                for inv in fixable
            )
            wiz.skipped_count = len(skipped)

    def _get_invoices(self):
        states = ['draft']
        if self.include_posted:
            states.append('posted')

        domain = [
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('journal_id.code', 'in', ['ECOM', 'WSH']),
            ('state', 'in', states),
        ]
        if self.date_from:
            domain.append(('invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('invoice_date', '<=', self.date_to))

        invoices = self.env['account.move'].search(domain)

        if self.include_paid:
            return invoices, self.env['account.move']

        paid = invoices.filtered(
            lambda m: m.payment_state in ['paid', 'in_payment', 'partial']
        )
        return invoices - paid, paid

    def _find_tax(self, country, company):
        if country.code == SINGAPORE_COUNTRY_CODE:
            names, label = TAX_SINGAPORE_NAMES, TAX_SINGAPORE_LABEL
        else:
            names, label = TAX_INTERNATIONAL_NAMES, TAX_INTERNATIONAL_LABEL

        for name in names:
            tax = self.env['account.tax'].search([
                ('name', '=', name),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', company.id),
                ('active', '=', True),
            ], limit=1)
            if tax:
                return tax

        return self.env['account.tax'].search([
            ('description', '=', label),
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', company.id),
            ('active', '=', True),
        ], limit=1)

    def _get_reconciled_payments(self, invoice):
        """Return list of (payment, amount) to re-reconcile after reset."""
        reconciled = []
        for line in invoice.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable' and l.reconciled
        ):
            for matched in line.matched_credit_ids:
                reconciled.append(matched.credit_move_id)
            for matched in line.matched_debit_ids:
                reconciled.append(matched.debit_move_id)
        return reconciled

    def _fix_invoice(self, invoice, tax):
        """Reset to draft, fix tax, re-post, restore reconciliation."""
        payment_state = invoice.payment_state
        is_paid = payment_state in ['paid', 'in_payment', 'partial']

        # Save payment move lines before unreconciling
        reconciled_lines = self._get_reconciled_payments(invoice) if is_paid else []

        invoice.sudo().button_draft()

        invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == 'product'
        ).write({'tax_ids': [(6, 0, tax.ids)]})

        bank_id = invoice.partner_bank_id
        if bank_id and not bank_id.allow_out_payment:
            invoice.partner_bank_id = False
        invoice.sudo().action_post()
        if bank_id and not invoice.partner_bank_id:
            invoice.partner_bank_id = bank_id

        # Re-reconcile with original payments
        if reconciled_lines:
            receivable_line = invoice.line_ids.filtered(
                lambda l: l.account_id.account_type == 'asset_receivable'
                and not l.reconciled
            )
            if receivable_line:
                (receivable_line + self.env['account.move.line'].union(*[
                    self.env['account.move.line'].browse(l.id)
                    for l in reconciled_lines
                    if not l.reconciled
                ])).reconcile()

    def action_export_list(self):
        self.ensure_one()
        fixable, _ = self._get_invoices()

        # Precompute SG/non-SG taxes once to avoid repeated DB queries in loop
        company = self.env.company
        sg_tax = self._find_tax(
            self.env.ref('base.sg', raise_if_not_found=False)
            or self.env['res.country'].search([('code', '=', 'SG')], limit=1),
            company,
        )
        zr_tax = self.env['account.tax'].search([
            ('name', 'in', TAX_INTERNATIONAL_NAMES),
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', company.id),
            ('active', '=', True),
        ], limit=1)

        # Prefetch all needed fields in bulk
        fixable.read(['name', 'invoice_date', 'state', 'payment_state',
                      'partner_id', 'partner_shipping_id'])
        fixable.mapped('partner_id.name')
        fixable.mapped('partner_shipping_id.country_id.code')
        fixable.mapped('invoice_line_ids.display_type')
        fixable.mapped('invoice_line_ids.tax_ids.name')

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Invoice Number', 'Customer', 'Invoice Date',
            'State', 'Payment State', 'Shipping Country',
            'Current Tax', 'Correct Tax',
        ])

        for invoice in fixable:
            country = invoice.partner_shipping_id.country_id
            current_taxes = ', '.join(
                invoice.invoice_line_ids.filtered(
                    lambda l: l.display_type == 'product'
                ).mapped('tax_ids.name')
            )
            if country.code == SINGAPORE_COUNTRY_CODE:
                correct_tax = sg_tax
            elif country:
                correct_tax = zr_tax
            else:
                correct_tax = self.env['account.tax']

            writer.writerow([
                invoice.name,
                invoice.partner_id.name,
                invoice.invoice_date,
                invoice.state,
                invoice.payment_state,
                country.name if country else '',
                current_taxes,
                correct_tax.name if correct_tax else 'NOT FOUND',
            ])

        csv_bytes = output.getvalue().encode('utf-8-sig')
        attachment = self.env['ir.attachment'].create({
            'name': 'ecom_invoices_to_fix.csv',
            'type': 'binary',
            'datas': base64.b64encode(csv_bytes),
            'mimetype': 'text/csv',
            'res_model': self._name,
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def action_fix_taxes(self):
        self.ensure_one()
        fixable, skipped = self._get_invoices()

        if not fixable:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Nothing to fix'),
                    'message': _('No invoices found in the selected date range.'),
                    'type': 'warning',
                    'sticky': False,
                },
            }

        fixed = no_country = no_tax = errors = 0

        for invoice in fixable:
            country = invoice.partner_shipping_id.country_id
            if not country:
                no_country += 1
                continue

            tax = self._find_tax(country, invoice.company_id)
            if not tax:
                no_tax += 1
                continue

            try:
                self._fix_invoice(invoice, tax)
                fixed += 1
            except Exception:
                errors += 1

        parts = [_('%d invoices fixed.') % fixed]
        if skipped:
            parts.append(_('%d invoices skipped (excluded by filter).') % len(skipped))
        if no_country:
            parts.append(_('%d skipped: no shipping country.') % no_country)
        if no_tax:
            parts.append(_('%d skipped: tax not found.') % no_tax)
        if errors:
            parts.append(_('%d errors (check manually).') % errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('GST Tax Fix Complete'),
                'message': ' '.join(parts),
                'type': 'success',
                'sticky': True,
            },
        }
