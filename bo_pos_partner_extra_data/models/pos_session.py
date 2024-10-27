from odoo import models, fields, api, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].extend(["birthdate", "gender", "married", "children","date_wedding","no_children"])
        return result

