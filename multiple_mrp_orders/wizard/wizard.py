
from odoo import models, fields, api, _


class MrpProductWizard(models.TransientModel):
    """Create a new wizard mrp.product.produce.wizard"""
    _name = 'mrp.product.produce.wizard'
    _description = 'MRP Product Produce Wizard'

    produce_line_ids = fields.One2many('mrp.product.produce.wizard.line', 'product_produce_id',
                                       string='Product to Track')

    # Method to check availability and produce the products for mrp orders
    def action_check_availability_produce(self):
        for line in self.produce_line_ids:
            # skip cancelled, done and to_close MO's
            if line.production_id.state in ('cancel', 'done', 'to_close'):
                continue
            elif line.production_id.state == 'draft':
                line.production_id.action_confirm()
                line.production_id.with_context({'default_produce_line_ids':None}).action_assign()
            elif line.production_id.state == 'confirmed':
                line.production_id.action_assign()
            wiz_data = self.env['mrp.product.produce'].with_context({
                'active_id': line.production_id.id,
                'active_ids': [line.production_id.id],
            }).default_get(['production_id', 'product_id', 'product_uom_id', 'serial', 'consumption'])
            if not wiz_data:
                wiz_data = {}
            wiz_data['qty_producing'] = line.qty
            wiz_data['consumption'] = 'strict'
            produce_wizard = self.env['mrp.product.produce'].with_context({
                'active_id': line.production_id.id,
                'active_ids': [line.production_id.id],
            }).create(wiz_data)
            line_values = produce_wizard._update_workorder_lines()
            self.env['mrp.product.produce.line'].create(line_values['to_create'])
            produce_wizard.do_produce()

    # Method to mark the mrp orders as done
    def action_done(self):
        self.action_check_availability_produce()
        for line in self.produce_line_ids.mapped('production_id'):
            line.button_mark_done()


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Method for the wizard check availability and produce
    def action_product_availability_produce_show_wizard(self):
        production_ids = self.env['mrp.production'].browse(self._context.get('active_ids', False))
        lines = []
        for line in production_ids:
            vals = (0, 0, {
                'production_id': line.id,
                'product_id': line.product_id.id,
                'qty': line.product_qty
            })
            lines.append(vals)
        return {'type': 'ir.actions.act_window',
                'name': _('Produce'),
                'res_model': 'mrp.product.produce.wizard',
                'target': 'new',
                'view_id': self.env.ref('multiple_mrp_orders.view_mrp_product_availability_wizard').id,
                'view_mode': 'form',
                'context': {'default_produce_line_ids': lines}
                }

    # Method for the wizard Mark as Done
    def action_done_show_wizard(self):
        production_ids = self.env['mrp.production'].browse(self._context.get('active_ids', False))
        lines = []
        for line in production_ids:
            vals = (0, 0, {
                'production_id': line.id,
                'product_id': line.product_id.id,
                'qty': line.product_qty
            })
            lines.append(vals)
        return {'type': 'ir.actions.act_window',
                'name': _('Mark as Done'),
                'res_model': 'mrp.product.produce.wizard',
                'target': 'new',
                'view_id': self.env.ref('multiple_mrp_orders.view_mrp_product_done_wizard').id,
                'view_mode': 'form',
                'context': {'default_produce_line_ids': lines}
                }
                
    def action_assign(self):
        print(f"################################ {self._context}")
        super().action_assign()


class MrpProductProduceWizardLine(models.TransientModel):
    _name = "mrp.product.produce.wizard.line"
    _description = "Record Production Line"

    product_produce_id = fields.Many2one('mrp.product.produce.wizard')
    production_id = fields.Many2one('mrp.production')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Quantity')
