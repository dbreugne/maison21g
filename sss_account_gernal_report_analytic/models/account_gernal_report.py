# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"

    @api.model
    def _get_columns_name(self, options):
        res = super(AccountGeneralLedgerReport, self)._get_columns_name(options)
        res.insert(4, {'name': 'Analytic'})
        return res

    @api.model
    def _get_query_amls(self, options, expanded_account, offset=None, limit=None):
        ''' Construct a query retrieving the account.move.lines when expanding a report line with or without the load
        more.
        :param options:             The report options.
        :param expanded_account:    The account.account record corresponding to the expanded line.
        :param offset:              The offset of the query (used by the load more).
        :param limit:               The limit of the query (used by the load more).
        :return:                    (query, params)
        '''

        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        # Get sums for the account move lines.
        # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
        if expanded_account:
            domain = [('account_id', '=', expanded_account.id)]
        elif unfold_all:
            domain = []
        elif options['unfolded_lines']:
            domain = [('account_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

        new_options = self._force_strict_range(options)
        tables, where_clause, where_params = self._query_get(new_options, domain=domain)
        ct_query = self._get_query_currency_table(options)
        query = '''
            SELECT
                account_move_line.id,
                account_move_line.date,
                account_move_line.date_maturity,
                account_move_line.name,
                account_move_line.ref,
                account_move_line.company_id,
                account_move_line.account_id,
                account_move_line.payment_id,
                account_move_line.partner_id,
                account_move_line.currency_id,
                account_move_line.amount_currency,
                aa.name                                                 AS analytic_account,
                aa.code                                                 AS analytic_account_code,
                ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                account_move_line__move_id.name         AS move_name,
                company.currency_id                     AS company_currency_id,
                partner.name                            AS partner_name,
                account_move_line__move_id.type         AS move_type,
                account.code                            AS account_code,
                account.name                            AS account_name,
                journal.code                            AS journal_code,
                journal.name                            AS journal_name,
                full_rec.name                           AS full_rec_name
            FROM account_move_line
            LEFT JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN res_company company               ON company.id = account_move_line.company_id
            LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
            LEFT JOIN account_account account           ON account.id = account_move_line.account_id
            LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
            LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
            LEFT JOIN account_analytic_account AS aa ON aa.id = account_move_line.analytic_account_id
            WHERE %s
            ORDER BY account_move_line.date, account_move_line.id
        ''' % (ct_query, where_clause)

        if offset:
            query += ' OFFSET %s '
            where_params.append(offset)
        if limit:
            query += ' LIMIT %s '
            where_params.append(limit)

        return query, where_params

    @api.model
    def _get_initial_balance_line(self, options, account, amount_currency, debit, credit, balance):
        res = super()._get_initial_balance_line(options, account, amount_currency, debit, credit, balance)
        res.update({'colspan': 5})
        return res

    @api.model
    def _get_account_title_line(self, options, account, amount_currency, debit, credit, balance, has_lines):
        res = super()._get_account_title_line(options, account, amount_currency, debit, credit, balance, has_lines)
        res.update({'colspan': 5})
        return res

    @api.model
    def _get_aml_line(self, options, account, aml, cumulated_balance):
        res = super()._get_aml_line(options, account, aml, cumulated_balance)
        # if aml['analytic_account'] and aml['analytic_account_code']:

        #     accoun_name = "[" + aml['analytic_account_code'] + "]" + "-" + aml['analytic_account']
        # else:
        #     accoun_name = ""
        res.get('columns').insert(3, {'name': aml['analytic_account'], 'title': aml['analytic_account'], 'class': 'whitespace_print'})
        return res

    @api.model
    def _get_account_total_line(self, options, account, amount_currency, debit, credit, balance):
        res = super()._get_account_total_line(options, account, amount_currency, debit, credit, balance)
        res.update({'colspan': 5})
        return res

    @api.model
    def _get_total_line(self, options, debit, credit, balance):
        res = super(AccountGeneralLedgerReport, self)._get_total_line(options, debit, credit, balance)
        res.update({'colspan': 6})
        return res
