# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from datetime import timedelta, datetime
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError


class InvoiceSplitWizard(models.TransientModel):
    _name = "invoice.split.wizard"
    _description = "Invoice Split Wizard"
    split_option = fields.Selection([('new', 'New'), ('existing', 'Existing')], string='Split Option', default='new')
    invoice_id = fields.Many2one('account.move', string='Invoice',
                                 domain=[('state', 'not in', ('cancel', 'paid', 'open', 'posted'))])
    invoice_ids = fields.Many2many('account.move', string='invoice')

    @api.model
    def default_get(self, fields):
        res = super(InvoiceSplitWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        if active_ids:
            invoice_active_ids = self.env['account.move'].browse(active_ids)
            invoice_move_type_ids = self.env['account.move'].search([('move_type','=',invoice_active_ids.move_type)])
            res.update({'invoice_ids':invoice_move_type_ids})
        return res

    def split_invoice(self):
        if self.invoice_id.id == self.env.context.get('active_id') or False:
            raise ValidationError(_("Cannot Split Lines in Same Invoice"))
        else:
            active_invoice_id = self.env['account.move'].browse(self._context.get('active_id'))
            return active_invoice_id.make_split_invoice(self.split_option, self.invoice_id.id, is_extract=False)