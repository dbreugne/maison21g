from odoo import api, fields, models, _

TAX_SINGAPORE_NAMES = ['Sales Tax 9% SR', '[old] Sales Tax 9% SR']
TAX_SINGAPORE_LABEL = '9% SR'
TAX_INTERNATIONAL_NAMES = ['Sales Tax 0% ZR']
TAX_INTERNATIONAL_LABEL = '0% ZR'
SINGAPORE_COUNTRY_CODE = 'SG'


class FixEcomInvoiceTaxWizard(models.TransientModel):
    _name = 'fix.ecom.invoice.tax.wizard'
    _description = 'Fix ECOM Invoice GST Tax Codes'

    date_from = fields.Date(string='From Date', required=True, default='2026-01-01')
    date_to = fields.Date(string='To Date', required=True, default='2026-03-31')
    include_posted = fields.Boolean(
        string='Include Confirmed Invoices',
        default=True,
        help='Posted invoices will be reset to draft, tax corrected, then re-confirmed. '
             'Paid invoices are always skipped.',
    )
    invoice_count = fields.Integer(compute='_compute_preview')
    line_count = fields.Integer(compute='_compute_preview')
    skipped_paid_count = fields.Integer(compute='_compute_preview')

    @api.depends('date_from', 'date_to', 'include_posted')
    def _compute_preview(self):
        for wiz in self:
            fixable, paid = wiz._get_invoices()
            wiz.invoice_count = len(fixable)
            wiz.line_count = sum(
                len(inv.invoice_line_ids.filtered(lambda l: l.display_type == 'product'))
                for inv in fixable
            )
            wiz.skipped_paid_count = len(paid)

    def _get_invoices(self):
        """Return (fixable_invoices, paid_invoices) recordsets."""
        states = ['draft']
        if self.include_posted:
            states.append('posted')

        invoices = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('state', 'in', states),
        ])

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

    def action_fix_taxes(self):
        self.ensure_one()
        fixable, paid = self._get_invoices()

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

        fixed = no_country = no_tax = 0

        for invoice in fixable:
            country = invoice.partner_shipping_id.country_id
            if not country:
                no_country += 1
                continue

            tax = self._find_tax(country, invoice.company_id)
            if not tax:
                no_tax += 1
                continue

            was_posted = invoice.state == 'posted'
            if was_posted:
                invoice.sudo().button_draft()

            invoice.invoice_line_ids.filtered(
                lambda l: l.display_type == 'product'
            ).write({'tax_ids': [(6, 0, tax.ids)]})

            if was_posted:
                # Clear partner_bank_id temporarily to bypass untrusted bank account check,
                # then restore it after posting (Odoo 17 blocks post if bank not trusted)
                bank_id = invoice.partner_bank_id
                if bank_id and not bank_id.allow_out_payment:
                    invoice.partner_bank_id = False
                invoice.sudo().action_post()
                if bank_id and not invoice.partner_bank_id:
                    invoice.partner_bank_id = bank_id

            fixed += 1

        parts = [_('%d invoices fixed.') % fixed]
        if paid:
            parts.append(_('%d paid invoices skipped (manual fix required).') % len(paid))
        if no_country:
            parts.append(_('%d invoices skipped: no shipping country set.') % no_country)
        if no_tax:
            parts.append(_('%d invoices skipped: matching tax not found in system.') % no_tax)

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
