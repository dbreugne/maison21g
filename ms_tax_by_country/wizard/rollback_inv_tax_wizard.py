from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RollbackInvTaxWizard(models.TransientModel):
    _name = 'rollback.inv.tax.wizard'
    _description = 'Rollback Incorrectly Overwritten Invoice Tax Codes'

    cutoff_date = fields.Datetime(
        string='Changes Since',
        required=True,
        default='2026-05-09 00:00:00',
        help='Datetime when the bad module update was deployed. All tax changes after this date on invoices with a previous tax will be reverted.',
    )
    affected_count = fields.Integer(compute='_compute_preview', string='Invoices Affected')
    paid_count = fields.Integer(compute='_compute_preview', string='Paid (Cannot Auto-Fix)')
    preview_text = fields.Text(compute='_compute_preview', string='Preview')

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
            for inv in fixable[:20]:
                c = next((x for x in changes if x['invoice_id'] == inv.id), None)
                orig = c['original_tax'] if c else '?'
                lines.append(f"  {inv.name}  [{inv.state}]  original tax: {orig}")
            if len(fixable) > 20:
                lines.append(f"  ... and {len(fixable) - 20} more")
            if paid:
                lines.append(f"\nPAID (manual fix needed): {', '.join(paid.mapped('name'))}")
            wiz.preview_text = '\n'.join(lines) if lines else 'No invoices found to rollback.'

    def _get_affected_changes(self):
        """
        Return list of dicts: {invoice_id, original_tax (name), new_tax (name)}
        Only includes invoices where a pre-existing tax was overwritten (old_value_char not empty).
        """
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

        # Build map: invoice_id -> list of (original_tax_name, new_tax_name)
        inv_changes = {}
        for t in trackings:
            inv_id = t.mail_message_id.res_id
            if inv_id not in inv_changes:
                inv_changes[inv_id] = []
            inv_changes[inv_id].append({
                'original_tax': t.old_value_char,
                'new_tax': t.new_value_char,
            })

        result = []
        for inv_id, changes in inv_changes.items():
            # Use the most common original tax for this invoice
            orig = changes[0]['original_tax']
            result.append({
                'invoice_id': inv_id,
                'original_tax': orig,
                'new_tax': changes[0]['new_tax'],
                'all_originals': changes,
            })
        return result

    def action_rollback(self):
        self.ensure_one()
        changes = self._get_affected_changes()
        if not changes:
            raise UserError(_('No affected invoices found after the given date.'))

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

            original_tax_name = change['original_tax']
            original_tax = self.env['account.tax'].search([
                ('name', '=', original_tax_name),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', invoice.company_id.id),
            ], limit=1)

            if not original_tax:
                errors.append(f"{invoice.name}: tax '{original_tax_name}' not found in database")
                continue

            was_posted = invoice.state == 'posted'
            try:
                if was_posted:
                    invoice.button_draft()

                product_lines = invoice.invoice_line_ids.filtered(
                    lambda l: l.display_type == 'product'
                )
                product_lines.write({'tax_ids': [(6, 0, original_tax.ids)]})

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
            parts.append(_('Errors:\n') + '\n'.join(errors))

        msg_type = 'success' if not errors else 'warning'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Rollback Complete'),
                'message': '\n'.join(parts),
                'type': msg_type,
                'sticky': True,
            },
        }
