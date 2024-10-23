# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger.report.handler"

    @api.model
    def _get_columns_name(self, options):
        res = super(AccountGeneralLedgerReport, self)._get_columns_name(options)
        res.insert(4, {'name': 'Analytic'})
        return res

    def _get_query_amls(self, report, options, expanded_account_ids, offset=0, limit=None):
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
        if expanded_account_ids:
            domain = [('account_id', 'in', expanded_account_ids)]
        elif unfold_all:
            domain = []
        elif options['unfolded_lines']:
            domain = [('account_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]


        queries = []
        all_params = []
        lang = self.env.user.lang or get_lang(self.env).code
        journal_name = f"COALESCE(journal.name->>'{lang}', journal.name->>'en_US')" if \
            self.pool['account.journal'].name.translate else 'journal.name'
        account_name = f"COALESCE(account.name->>'{lang}', account.name->>'en_US')" if \
            self.pool['account.account'].name.translate else 'account.name'
        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            # Get sums for the account move lines.
            # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
            tables, where_clause, where_params = report._query_get(group_options, domain=domain, date_scope='strict_range')
            ct_query = report._get_query_currency_table(group_options)
            query = f'''
                (SELECT
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
                    COALESCE(account_move_line.invoice_date, account_move_line.date)                 AS invoice_date,
                    ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                    ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                    ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                    move.name                               AS move_name,
                    company.currency_id                     AS company_currency_id,
                    partner.name                            AS partner_name,
                    move.move_type                          AS move_type,
                    account.code                            AS account_code,
                    {account_name}                          AS account_name,
                    journal.code                            AS journal_code,
                    {journal_name}                          AS journal_name,
                    full_rec.id                             AS full_rec_name,
                    %s                                      AS column_group_key
                FROM {tables}
                JOIN account_move move                      ON move.id = account_move_line.move_id
                LEFT JOIN {ct_query}                        ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
                WHERE {where_clause}
                ORDER BY account_move_line.date, account_move_line.move_name, account_move_line.id)
            '''

            queries.append(query)
            all_params.append(column_group_key)
            all_params += where_params

        full_query = " UNION ALL ".join(queries)

        if offset:
            full_query += ' OFFSET %s '
            all_params.append(offset)
        if limit:
            full_query += ' LIMIT %s '
            all_params.append(limit)

        return (full_query, all_params)

    @api.model
    def _get_initial_balance_line(self, options, account, amount_currency, debit, credit, balance):
        res = super()._get_initial_balance_line(options, account, amount_currency, debit, credit, balance)
        res.update({'colspan': 5})
        return res

    def _get_account_title_line(self, report, options, account, has_lines, eval_dict):
        res = super()._get_account_title_line(report, options, account, has_lines, eval_dict)
        res.update({'colspan': 5})
        return res

    def _get_aml_line(self, report, parent_line_id, options, eval_dict, init_bal_by_col_group):
        res = super()._get_aml_line(report, parent_line_id, options, eval_dict, init_bal_by_col_group)
        # if aml['analytic_account'] and aml['analytic_account_code']:

        #     accoun_name = "[" + aml['analytic_account_code'] + "]" + "-" + aml['analytic_account']
        # else:
        #     accoun_name = ""
        #res.get('columns').insert(3, {'name': eval_dict['analytic_account'], 'title': eval_dict['analytic_account'], 'class': 'whitespace_print'})
        return res

    @api.model
    def _get_account_total_line(self, options, account, amount_currency, debit, credit, balance):
        res = super()._get_account_total_line(options, account, amount_currency, debit, credit, balance)
        res.update({'colspan': 5})
        return res

    @api.model
    def _get_total_line(self, report, options, eval_dict):
        res = super(AccountGeneralLedgerReport, self)._get_total_line( report, options, eval_dict)
        res.update({'colspan': 6})
        return res
