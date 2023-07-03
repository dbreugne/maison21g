from odoo import models, fields, api, _
from odoo.exceptions import UserError

from itertools import groupby

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_bottle_line(self):
			# assign bottle line only for scent lines that didn't have any bottle line      
      for order in self:
        # bottle_lines = pos.lines.filtered(lambda ln: ln.is_bottle)
        # scent_lines = pos.lines.filtered(lambda ln: ln.is_scent)
        # related_bottle = scent
        # if len(scent_lines) and : 
        bottle_line_idx = False
        idx = 0
        for line in order.lines:
          if line.is_bottle:
            bottle_line_idx = idx
          if line.is_scent and (not line.bottle_line_idx or not line.bottle_line_id.id):
            line.bottle_line_idx = bottle_line_idx
            if not line.bottle_line_id.id:
              # ensure computation called                 
              line._get_bottle_line()
          idx += 1

    # def action_bottle_line(self):
    #     for pos in self:
    #         header_name = pos.lines.filtered(lambda r: r.is_bottle == False and r.is_scent == False).mapped('name')
    #         res_name = []
    #         res_product = []
    #         seq = 1
    #         for name in header_name:
    #             for line in pos.lines:
    #                 if not any(item['order_line_id'] == line.id for item in res_product):
    #                     if (line.name == name and line.display_type == 'line_section'):
    #                         res_name.append({
    #                             'idx': seq,
    #                             'order_id': pos.id,
    #                             'name': line.name,
    #                         })
    #                         seq += 1
    #                         break
    #                 # if not any(item['name'] != name for item in res_name):
    #                     if (line.is_bottle != False or line.is_scent != False):
    #                         res_product.append({
    #                             'idx': seq,
    #                             'order_line_id': line.id,
    #                             'product_id': line.product_id.id,
    #                         })
    #                     # seq += 1
    #             # continue
    #                 # result = res_name + res_product
    #         return pos._running_query_for_update(res_product)

    def _running_query_for_update(self, res_product):
        grouped_data = []
        for key, group in groupby(res_product, key=lambda x: x['idx']):
            grouped_data.append({'idx': key, 'lines': list(group)})

        for data in grouped_data:
            list_product = [x['product_id'] for x in data['lines']]
            product_obj = self.env['product.product'].browse(list_product).filtered(lambda l: l.is_bottle == True)
            bottle_line_id = [x['order_line_id'] for x in data['lines'] if x['product_id'] == product_obj.id]
            order_line_id = [x['order_line_id'] for x in data['lines'] if x['product_id'] != product_obj.id]

            query = """
                UPDATE pos_order_line 
                SET bottle_line_id = %s 
                WHERE order_id = %s
                AND id IN %s
            """
            self.env.cr.execute(query, (bottle_line_id[0], self.id, tuple(order_line_id)))
            self.env.cr.commit()


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    bottle_line_id = fields.Many2one("pos.order.line", compute='_get_bottle_line', store=True)
    bottle_line_idx = fields.Char()
    bottle_product_id = fields.Many2one("product.product", related="bottle_line_id.product_id", store=True, string="Bottle Product")
    is_bottle = fields.Boolean(related="product_id.is_bottle" , store=True)
    is_scent = fields.Boolean(related="product_id.is_scent" , store=True)

    @api.depends('bottle_line_idx')
    def _get_bottle_line(self):
        if not self._context.get('module', False):
            for line in self:
                bottle_line = False
                if line.bottle_line_idx:
                    idx = int(line.bottle_line_idx)
                    bottle_line = line.order_id.lines[idx]
                if bottle_line:
                    line.bottle_line_id = bottle_line.id
