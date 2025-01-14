# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from contextlib import ExitStack, contextmanager
from odoo.tools import (
    format_amount,
)
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_splited = fields.Boolean(string='Is Splited')
    is_extracted = fields.Boolean(string='Is extracted')

    is_split_from = fields.Many2one("account.move", "Splited From")
    is_extracted_from = fields.Many2one("account.move", "Extracted From")


    split_count = fields.Integer('Split Count', default=0)
    extract_count = fields.Integer('Extract Count', default=0)

    
    # def _check_balanced(self):
    #     ''' Assert the move is fully balanced debit = credit.
    #     An error is raised if it's not the case.
    #     '''
    #     moves = self.filtered(lambda move: move.line_ids)
    #     if not moves:
    #         return
    #
    #     # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
    #     # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
    #     # It happens as the ORM makes the create with the 'no_recompute' statement.
    #     self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
    #     self.env['account.move'].flush(['journal_id'])
    #     self._cr.execute('''
    #         SELECT line.move_id, ROUND(SUM(debit - credit), currency.decimal_places)
    #         FROM account_move_line line
    #         JOIN account_move move ON move.id = line.move_id
    #         JOIN account_journal journal ON journal.id = move.journal_id
    #         JOIN res_company company ON company.id = journal.company_id
    #         JOIN res_currency currency ON currency.id = company.currency_id
    #         WHERE line.move_id IN %s
    #         GROUP BY line.move_id, currency.decimal_places
    #         HAVING ROUND(SUM(debit - credit), currency.decimal_places) != 0.0;
    #     ''', [tuple(self.ids)])
    #
    #     query_res = self._cr.fetchall()
    @contextmanager
    def _check_balanced(self, container):
        if self.env.user.has_group("bi_split_invoice.group_show_split_invoice_button"):
            ''' Assert the move is fully balanced debit = credit.
            An error is raised if it's not the case.
            '''

            with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
                yield
                if disabled:
                    return
                    
            if not self._context.get('skip_raise_error', False):
                super(AccountMove,self )._check_balanced(container)
            
        else:
            ''' Assert the move is fully balanced debit = credit.
            An error is raised if it's not the case.
            '''
            with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
                yield
                if disabled:
                    return


            unbalanced_moves = self._get_unbalanced_moves(container)
            if unbalanced_moves:
                error_msg = _("An error has occurred.")
                for move_id, sum_debit, sum_credit in unbalanced_moves:
                    move = self.browse(move_id)
                    error_msg += _(
                        "\n\n"
                        "The move (%s) is not balanced.\n"
                        "The total of debits equals %s and the total of credits equals %s.\n"
                        "You might want to specify a default account on journal \"%s\" to automatically balance each move.",
                        move.display_name,
                        format_amount(self.env, sum_debit, move.company_id.currency_id),
                        format_amount(self.env, sum_credit, move.company_id.currency_id),
                        move.journal_id.name)
                raise UserError(error_msg)

    def select_all(self):
        for record in self:
            if not record.invoice_line_ids:
                raise ValidationError(_('Sorry !!! \nPlease Create invoice Line.'))
            else:
                for move_line in record.invoice_line_ids:
                    move_line.invoice_split = True

    def unselect_all(self):
        for record in self:
            if not record.invoice_line_ids:
                raise ValidationError(_('Sorry !!! \nPlease Create invoice Line.'))
            else:
                for move_line in record.invoice_line_ids:
                    move_line.invoice_split = False

        return

    def split_invoice(self):
        for record in self:
            if not record.invoice_line_ids:
                raise ValidationError(_('Sorry !!! \nPlease Create invoice Line.'))
            else:
                if not any(line.invoice_split for line in self.invoice_line_ids):
                    raise ValidationError(_('Sorry !!! \nPlease Select invoice Line For Splitting.'))
                else:
                    return self.env.ref(
                        'bi_split_invoice.invoice_split_wizard_action').read()[0]

    def extract_invoice(self):
        if len(self.invoice_line_ids) == 0:
            raise ValidationError(_('Sorry !!! \nPlease Create invoice Line.'))
        if not any(line.invoice_split for line in self.invoice_line_ids):
            raise ValidationError(_('Sorry !!! \nPlease Select invoice Line For Splitting.'))
        else:
            return self.make_split_invoice(split_option=False, invoice=False, is_extract=True)

    def make_split_invoice(self, split_option=False, invoice=False, is_extract=False):
        make_split_invoice_id = self.env['account.move'].browse(invoice)
        if is_extract:
            split_option = 'new'
        if split_option == 'new':
            for record in self:
                count = 0
                for move_line in record.invoice_line_ids:
                    if move_line.invoice_split:
                        count += 1
                if count >= 1:
                    invoice = self.copy()
                    for line in invoice.invoice_line_ids:
                        if not line.invoice_split:
                            line.unlink()
                        else:
                            line.invoice_split = False

                    for mv in record.invoice_line_ids:
                        if mv.invoice_split:
                            if not is_extract:
                                self.env['account.move.line'].browse(mv.id).unlink()
                    if is_extract:
                        invoice.is_extracted = True
                        invoice.is_extracted_from = self.id
                        record.extract_count = int(self.extract_count) + 1
                    else:
                        invoice.is_splited = True
                        invoice.is_split_from = self.id
                        record.split_count = int(self.split_count) + 1
        else:
            for line in self.invoice_line_ids:
                if line.invoice_split:
                    make_split_invoice_id.sudo().with_context(skip_raise_error=True).write({
                        'invoice_line_ids': [(4, line.id)]})

            make_split_invoice_id.is_splited = True
            if make_split_invoice_id.is_split_from.id != self.id:
                self.split_count = int(self.split_count) + 1
            make_split_invoice_id.is_split_from = self.id
            return make_split_invoice_id


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_split = fields.Boolean(string='Split')
