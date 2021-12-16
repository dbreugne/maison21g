from odoo import models, fields,api


class product_template(models.Model):
    _inherit = 'product.template'

    is_product_pack = fields.Boolean("Is Product Pack")
    pack_product_ids = fields.One2many("pack.product",'product_new_name',String="Pack Products")


    @api.onchange('is_product_pack')
    def set_pos_category(self):
        if self.pos_categ_id.parent_id.name != 'Pack' and self.is_product_pack:
            categ_obj = self.env['pos.category']
            categ_id = categ_obj.search([('parent_id','=','Pack')])
            if categ_id:
                self.pos_categ_id = categ_id.id
            else:
                parent_categ_id  = categ_obj.search([('name','=','Pack')])
                if parent_categ_id:
                    categ_id = categ_obj.create({'name': 'Pack Products', 'parent_id': parent_categ_id.id})
                    self.pos_categ_id = categ_id.id
                else:
                    parent_id = categ_obj.create({'name':'Pack'})
                    categ_id = categ_obj.create({'name':'Pack Products','parent_id': parent_id.id})
                    self.pos_categ_id = categ_id.id
        else:
            if not self.is_product_pack:
                self.pos_categ_id = False



class product_product(models.Model):
    _inherit = 'product.product'


    @api.onchange('is_product_pack')
    def set_pos_category(self):
        if self.pos_categ_id.parent_id.name != 'Pack' and self.is_product_pack:
            categ_obj = self.env['pos.category']
            categ_id = categ_obj.search([('parent_id', '=', 'Pack')])
            if categ_id:
                self.pos_categ_id = categ_id.id
            else:
                parent_categ_id = categ_obj.search([('name', '=', 'Pack')])
                if parent_categ_id:
                    categ_id = categ_obj.create({'name': 'Pack Products', 'parent_id': parent_categ_id.id})
                    self.pos_categ_id = categ_id.id
                else:
                    parent_id = categ_obj.create({'name': 'Pack'})
                    categ_id = categ_obj.create({'name': 'Pack Products', 'parent_id': parent_id.id})
                    self.pos_categ_id = categ_id.id
        else:
            if not self.is_product_pack:
                self.pos_categ_id = False
