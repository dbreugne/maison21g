from odoo import api, models,fields,_
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta

class StockLocation(models.Model):

    _inherit = 'stock.location'

    mo_picking_type= fields.Many2one('stock.picking.type','Picking Type')



class MultiMRP(models.Model):
    """Create a new model multi.mrp"""
    _name = "multi.mrp"
    _description = "Multi MRP"

    @api.model
    def _get_default_picking_type(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', '=', company_id),
        ], limit=1).id

    name=fields.Char('Name',required=True)
    multimrp_order_line_ids = fields.One2many('mrpmulti.lines','multi_batch_id','Batch MRP Orders',help="Here listed only on-hand quantity of product less than or equal to zero.")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        default=_get_default_picking_type, required=True)



    def generate_mrp_batch(self):
        if len(self.multimrp_order_line_ids)==0:
            raise ValidationError(_('Cannot Create a Order without Line'))
        for record in self.multimrp_order_line_ids:
            vals={
                'product_id':record.product_id.id,
                # 'initial_qty':record.qty_produce,
                'location_dest_id':record.location_id.id,
                'date_planned_start':record.schedule_date,
                'bom_id':record.bom_id.id,
                'product_uom_id':record.product_uom_id.id,
                'origin':'Batch Processing'+" "+self.name,
                'product_qty':record.qty_produce,
                'location_src_id':record.location_src_id.id,
                'picking_type_id':record.picking_type_id.id
            }
            production_obj=self.env['mrp.production'].create(vals)
            production_obj._onchange_move_raw()
            # production_obj.action_confirm()

    @api.model
    def default_get(self, fields):
        res = super(MultiMRP, self).default_get(fields)
        company_id = self.env.context.get('default_company_id', self.env.user.company_id.id)

        mrp_lines = []
        product_rec = self.env['mrp.bom'].search([])
        # location_obj=self.en[]
        for all in product_rec:
            # qty_hand = all.product_tmpl_id.with_context({'location': all.product_tmpl_id.location_id}).qty_available
            # if qty_hand < 0:
            virtual_main = []
            virtual_parent_locations = self.env['stock.location'].search([('location_id', '=',  False), ('usage', '=', 'view')])
            if virtual_parent_locations:
                virtual_main = virtual_parent_locations.ids
            if virtual_main:
                location_obj = self.env['stock.location'].search([('usage','not in',['inventory','view']), ('location_id', 'not in', virtual_main)])
            else:
                location_obj = self.env['stock.location'].search([('usage', 'not in', ['inventory', 'view'])])
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', all.product_tmpl_id.id)])
            for location in location_obj:
                qty_hand = 0
                qty_reserved=0
                stock_qty_obj = self.env['stock.quant']
                stock_qty_lines = stock_qty_obj.search([('product_id', '=', product_id.id),
                                                        ("location_id", "=", location.id)])
                for row in stock_qty_lines:
                    qty_hand += row.quantity
                    qty_reserved += row.reserved_quantity
                if qty_hand < 0:
                    line = (0, 0, {
                        'product_id': product_id.id,
                        'product_uom_id': self.env['uom.uom'].search([], limit=1, order='id').id,
                        'schedule_date': datetime.today(),
                        'qty_hand': qty_hand,
                        'qty_reserved':qty_reserved,
                        'location_src_id':location.id,
                        # 'location_src_id': location.id,
                        'bom_id': self.env['mrp.bom']._bom_find(product=product_id,
                                                                picking_type=self.picking_type_id,
                                                                company_id=all.company_id.id, bom_type='normal').id,
                        'picking_type_id': location and location.mo_picking_type and location.mo_picking_type.id or False,
                        # 'picking_type_id': self.env['stock.picking.type'].search([
                        #     ('code', '=', 'mrp_operation'),
                        #     ('warehouse_id.company_id', '=', company_id),
                        # ], limit=1).id
                    })
                    mrp_lines.append(line)
            res.update({
                'multimrp_order_line_ids': mrp_lines,
            })
        return res

        # @api.model
    # def default_get(self, fields):
    #     res = super(MultiMRP, self).default_get(fields)
    #     company_id = self.env.context.get('default_company_id', self.env.company.id)
    #
    #     mrp_lines = []
    #     product_rec = self.env['mrp.bom'].search([])
    #     # location_obj=self.en[]
    #     for all in product_rec:
    #         qty_hand = all.product_tmpl_id.with_context({'location': all.product_tmpl_id.location_id}).qty_available
    #         if qty_hand < 0:
    #             for pro in all:
    #                 product_id = self.env['product.product'].search([('product_tmpl_id', '=', all.product_tmpl_id.id)])
    #                 # location_obj=self.env['stock.location'].search([])
    #                 # print("name",location_obj)
    #                 line = (0, 0, {
    #                     'product_id': product_id.id,
    #                     'product_uom_id': self.env['uom.uom'].search([], limit=1, order='id').id,
    #                     'schedule_date':datetime.today(),
    #                     'qty_hand': all.product_tmpl_id.with_context(
    #                         {'location': all.product_tmpl_id.location_id}).qty_available,
    #                     'bom_id': self.env['mrp.bom']._bom_find(product=product_id,
    #                                                             picking_type=self.picking_type_id,
    #                                                             company_id=all.company_id.id, bom_type='normal').id,
    #                     'picking_type_id':self.env['stock.picking.type'].search([
    #                         ('code', '=', 'mrp_operation'),
    #                         ('warehouse_id.company_id', '=', company_id),
    #                     ], limit=1).id
    #                 })
    #                 mrp_lines.append(line)
    #                 res.update({
    #                     'multimrp_order_line_ids': mrp_lines,
    #                 })
    #     return res


class MultiMRPLine(models.Model):
    """Create a new model mrpmulti.lines"""
    _name = 'mrpmulti.lines'
    _description = 'MRP Multi Lines'

    @api.model
    def _get_default_picking_type(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', '=', company_id),
        ], limit=1).id

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    # @api.model
    # def _get_default_picking_type(self):
    #     company_id = self.env.context.get('default_company_id', self.env.company.id)
    #     return self.env['stock.picking.type'].search([
    #         ('code', '=', 'mrp_operation'),
    #         ('warehouse_id.company_id', '=', company_id),
    #     ], limit=1).id

    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id, required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")

    multi_batch_id = fields.Many2one('multi.mrp')
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="[('bom_ids', '!=', False), ('bom_ids.active', '=', True), ('bom_ids.type', '=', 'normal'), ('type', 'in', ['product', 'consu'])]",
        required=True)

    location_id = fields.Many2one('stock.location','Finished Location',domain="[('usage','=','internal')]",required=True)
    qty_produce =fields.Float('Qty Produced')
    varity_id=fields.Many2one('product.product','variant')
    schedule_date =fields.Date('Schedule Date')
    qty_hand = fields.Float('Quantity On Hand',)
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        help="Bill of Materials allow you to define the list of required raw materials to make a finished product.")
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    product_qty = fields.Float('Qty')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',related='location_src_id.mo_picking_type',required=True)
    location_src_id = fields.Many2one(
        'stock.location', 'Components Location',
        required=True,
        domain="[('usage','=','internal')]",
        help="Location where the system will look for components.")
    qty_reserved= fields.Float('Reserved Quantity',)

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        self.qty_hand = self.product_id.with_context({'location': self.product_id.location_id}).qty_available
        """ Finds UoM of changed product. """
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id,
                                                company_id=self.company_id.id, bom_type='normal')
            if bom:
                self.bom_id = bom.id
                self.product_qty = self.bom_id.product_qty
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}

