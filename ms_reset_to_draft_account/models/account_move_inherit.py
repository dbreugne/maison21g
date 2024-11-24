# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = 'account.move'

    
    def _compute_show_reset_to_draft_button(self):
        super()._compute_show_reset_to_draft_button()
        for move in self:
            move.show_reset_to_draft_button = (
                not move.restrict_mode_hash_table \
                and (move.state == 'cancel' or (move.state == 'posted' and not move.need_cancel_request))
            )
