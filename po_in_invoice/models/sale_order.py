from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # po_id = fields.Many2one("purchase.order", string="PO")
    # x_studio_po_number = fields.Char('PO Number')


    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['po_number'] = self.x_studio_po_number
        return invoice_vals