from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RollbackInvTaxWizard(models.TransientModel):
    _name = 'rollback.inv.tax.wizard'
    _description = 'Rollback Incorrectly Overwritten Invoice Tax Codes'

    cutoff_date = fields.Datetime(
        string='Changes Since',
        required=True,
        default='2026-05-10 00:00:00',
        help='Datetime when the bad module update ran. Tax changes after this date (on invoices that already had a tax) will be reverted.',
    )
    affected_count = fields.Integer(compute='_compute_preview', string='Invoices to Restore')
    paid_count = fields.Integer(compute='_compute_preview', string='Paid Invoices (Skipped)')
    preview_text = fields.Text(compute='_compute_preview', string='Invoice List')

    @api.depends('cutoff_date')
    def _compute_preview(self):
        for wiz in self:
            changes = wiz._get_affected_changes()
            inv_ids = list({c['invoice_id'] for c in changes})
            invoices = self.env['account.move'].browse(inv_ids)
            paid = invoices.filtered(lambda m: m.payment_state in ('paid', 'in_payment', 'partial'))
            fixable = invoices - paid
            wiz.affected_count = len(fixable)
            wiz.paid_count = len(paid)
            lines = []
            for inv in fixable[:30]:
                c = next((x for x in changes if x['invoice_id'] == inv.id), None)
                orig = c['original_tax'] if c else '?'
                lines.append(f"  {inv.name}  [{inv.state}]  → restore: {orig}")
            if len(fixable) > 30:
                lines.append(f"  ... and {len(fixable) - 30} more")
            if paid:
                lines.append(f"\nPAID (fix manually): {', '.join(paid.mapped('name'))}")
            wiz.preview_text = '\n'.join(lines) or 'No invoices found.'

    def _get_affected_changes(self):
        field = self.env['ir.model.fields'].search([
            ('model', '=', 'account.move.line'),
            ('name', '=', 'tax_ids'),
        ], limit=1)
        if not field:
            return []

        trackings = self.env['mail.tracking.value'].search([
            ('field_id', '=', field.id),
            ('mail_message_id.date', '>=', self.cutoff_date),
            ('mail_message_id.model', '=', 'account.move'),
            ('old_value_char', '!=', False),
            ('old_value_char', '!=', ''),
        ])

        inv_changes = {}
        for t in trackings:
            inv_id = t.mail_message_id.res_id
            if inv_id not in inv_changes:
                inv_changes[inv_id] = t.old_value_char

        return [{'invoice_id': inv_id, 'original_tax': orig_tax}
                for inv_id, orig_tax in inv_changes.items()]

    def action_rollback(self):
        self.ensure_one()
        changes = self._get_affected_changes()
        if not changes:
            raise UserError(_('No affected invoices found after %s.') % self.cutoff_date)

        fixed = 0
        skipped_paid = 0
        errors = []

        for change in changes:
            invoice = self.env['account.move'].browse(change['invoice_id'])
            if not invoice.exists():
                continue

            if invoice.payment_state in ('paid', 'in_payment', 'partial'):
                skipped_paid += 1
                continue

            original_tax = self.env['account.tax'].search([
                ('name', '=', change['original_tax']),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', invoice.company_id.id),
            ], limit=1)

            if not original_tax:
                errors.append(f"{invoice.name}: tax '{change['original_tax']}' not found")
                continue

            was_posted = invoice.state == 'posted'
            try:
                if was_posted:
                    invoice.button_draft()

                invoice.invoice_line_ids.filtered(
                    lambda l: l.display_type == 'product'
                ).write({'tax_ids': [(6, 0, original_tax.ids)]})

                if was_posted:
                    invoice.action_post()

                fixed += 1

            except Exception as e:
                errors.append(f"{invoice.name}: {e}")
                if was_posted:
                    try:
                        invoice.action_post()
                    except Exception:
                        pass

        parts = [_('%d invoices restored to original tax.') % fixed]
        if skipped_paid:
            parts.append(_('%d paid invoices skipped — fix manually.') % skipped_paid)
        if errors:
            parts.append('Errors:\n' + '\n'.join(errors))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Rollback Complete'),
                'message': '\n'.join(parts),
                'type': 'success' if not errors else 'warning',
                'sticky': True,
            },
        }
