# -*- coding: utf-8 -*-

from odoo import models, api, _, _lt, fields
import logging
from odoo.tools.misc import format_date, get_lang


_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.account'

    show_in_partner_ledger = fields.Boolean(string="Show In Partner Ledger Report", )


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger.report.handler"

    def _get_query_sums(self, options):
        """ Construct a query retrieving all the aggregated sums to build the report. It includes:
        - sums for all partners.
        - sums for the initial balances.
        :param options:             The report options.
        :return:                    (query, params)
        """
        params = []
        queries = []
        report = self.env.ref('account_reports.partner_ledger_report')

        # Create the currency table.
        ct_query = self.env['res.currency']._get_query_currency_table(options)
        is_show_account = self.env['account.account'].search(
            [('account_type', 'in', ['asset_receivable', 'asset_payable']),
             ('show_in_partner_ledger', '=', True)], limit=1)
        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            tables, where_clause, where_params = report._query_get(column_group_options, 'normal')
            params.append(column_group_key)
            params += where_params
            if is_show_account:
                queries.append(f"""
                    SELECT
                        account_move_line.partner_id                                                          AS groupby,
                        %s                                                                                    AS column_group_key,
                        SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                        SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                        SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                    FROM {tables}
                    LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                    LEFT JOIN account_account account ON account.id = account_move_line.account_id
                    WHERE {where_clause} AND account.show_in_partner_ledger is true
                    GROUP BY account_move_line.partner_id
                """)
            else:
                queries.append(f"""
                               SELECT
                                   account_move_line.partner_id                                                          AS groupby,
                                   %s                                                                                    AS column_group_key,
                                   SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                                   SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                                   SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                               FROM {tables}
                               LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                               WHERE {where_clause}
                               GROUP BY account_move_line.partner_id
                           """)

        return ' UNION ALL '.join(queries), params

    def _get_aml_values(self, options, partner_ids, offset=0, limit=None):
        rslt = {partner_id: [] for partner_id in partner_ids}

        partner_ids_wo_none = [x for x in partner_ids if x]
        directly_linked_aml_partner_clauses = []
        directly_linked_aml_partner_params = []
        indirectly_linked_aml_partner_params = []
        indirectly_linked_aml_partner_clause = 'aml_with_partner.partner_id IS NOT NULL'
        if None in partner_ids:
            directly_linked_aml_partner_clauses.append('account_move_line.partner_id IS NULL')
        if partner_ids_wo_none:
            directly_linked_aml_partner_clauses.append('account_move_line.partner_id IN %s')
            directly_linked_aml_partner_params.append(tuple(partner_ids_wo_none))
            indirectly_linked_aml_partner_clause = 'aml_with_partner.partner_id IN %s'
            indirectly_linked_aml_partner_params.append(tuple(partner_ids_wo_none))
        directly_linked_aml_partner_clause = '(' + ' OR '.join(directly_linked_aml_partner_clauses) + ')'

        ct_query = self.env['res.currency']._get_query_currency_table(options)
        queries = []
        all_params = []
        lang = self.env.lang or get_lang(self.env).code
        journal_name = f"COALESCE(journal.name->>'{lang}', journal.name->>'en_US')" if \
            self.pool['account.journal'].name.translate else 'journal.name'
        account_name = f"COALESCE(account.name->>'{lang}', account.name->>'en_US')" if \
            self.pool['account.account'].name.translate else 'account.name'
        report = self.env.ref('account_reports.partner_ledger_report')
        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            tables, where_clause, where_params = report._query_get(group_options, 'strict_range')

            all_params += [
                column_group_key,
                *where_params,
                *directly_linked_aml_partner_params,
                column_group_key,
                *indirectly_linked_aml_partner_params,
                *where_params,
                group_options['date']['date_from'],
                group_options['date']['date_to'],
            ]

            is_show_account = self.env['account.account'].search(
                [('account_type', 'in', ['asset_receivable', 'asset_payable']),
                 ('show_in_partner_ledger', '=', True)])

            if is_show_account:
                # For the move lines directly linked to this partner
                queries.append(f'''
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
                        account_move_line.matching_number,
                        ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                        ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                        ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                        account_move.name                                                                AS move_name,
                        account_move.move_type                                                           AS move_type,
                        account.code                                                                     AS account_code,
                        {account_name}                                                                   AS account_name,
                        journal.code                                                                     AS journal_code,
                        {journal_name}                                                                   AS journal_name,
                        %s                                                                               AS column_group_key,
                        'directly_linked_aml'                                                            AS key
                    FROM {tables}
                    JOIN account_move ON account_move.id = account_move_line.move_id
                    LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                    LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                    LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                    LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                    LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                    WHERE {where_clause} AND {directly_linked_aml_partner_clause} AND account.show_in_partner_ledger is true
                    ORDER BY account_move_line.date, account_move_line.id
                ''')

                # For the move lines linked to no partner, but reconciled with this partner. They will appear in grey in the report
                queries.append(f'''
                    SELECT
                        account_move_line.id,
                        account_move_line.date,
                        account_move_line.date_maturity,
                        account_move_line.name,
                        account_move_line.ref,
                        account_move_line.company_id,
                        account_move_line.account_id,
                        account_move_line.payment_id,
                        aml_with_partner.partner_id,
                        account_move_line.currency_id,
                        account_move_line.amount_currency,
                        account_move_line.matching_number,
                        CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE ROUND(
                            partial.amount * currency_table.rate, currency_table.precision
                        ) END                                                                               AS debit, 
                        CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE ROUND(
                            partial.amount * currency_table.rate, currency_table.precision
                        ) END                                                                               AS credit, 
                        - sign(aml_with_partner.balance) * ROUND(
                            partial.amount * currency_table.rate, currency_table.precision
                        )                                                                                   AS balance, 
                        account_move.name                                                                   AS move_name,
                        account_move.move_type                                                              AS move_type,
                        account.code                                                                        AS account_code,
                        {account_name}                                                                      AS account_name,
                        journal.code                                                                        AS journal_code,
                        {journal_name}                                                                      AS journal_name,
                        %s                                                                                  AS column_group_key,
                        'indirectly_linked_aml'                                                             AS key
                    FROM {tables}
                        LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id,
                        account_partial_reconcile partial,
                        account_move,
                        account_move_line aml_with_partner,
                        account_journal journal,
                        account_account account
                    WHERE
                        (account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id)
                        AND account_move_line.partner_id IS NULL
                        AND account_move.id = account_move_line.move_id
                        AND (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                        AND {indirectly_linked_aml_partner_clause}
                        AND journal.id = account_move_line.journal_id
                        AND account.id = account_move_line.account_id
                        AND {where_clause}
                        AND partial.max_date BETWEEN %s AND %s AND account.show_in_partner_ledger is true
                    ORDER BY account_move_line.date, account_move_line.id
                ''')
            else:
                # For the move lines directly linked to this partner
                queries.append(f'''
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
                                   account_move_line.matching_number,
                                   ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                                   ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                                   ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                                   account_move.name                                                                AS move_name,
                                   account_move.move_type                                                           AS move_type,
                                   account.code                                                                     AS account_code,
                                   {account_name}                                                                   AS account_name,
                                   journal.code                                                                     AS journal_code,
                                   {journal_name}                                                                   AS journal_name,
                                   %s                                                                               AS column_group_key,
                                   'directly_linked_aml'                                                            AS key
                               FROM {tables}
                               JOIN account_move ON account_move.id = account_move_line.move_id
                               LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                               LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                               LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                               LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                               LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                               WHERE {where_clause} AND {directly_linked_aml_partner_clause}
                               ORDER BY account_move_line.date, account_move_line.id
                           ''')

                # For the move lines linked to no partner, but reconciled with this partner. They will appear in grey in the report
                queries.append(f'''
                               SELECT
                                   account_move_line.id,
                                   account_move_line.date,
                                   account_move_line.date_maturity,
                                   account_move_line.name,
                                   account_move_line.ref,
                                   account_move_line.company_id,
                                   account_move_line.account_id,
                                   account_move_line.payment_id,
                                   aml_with_partner.partner_id,
                                   account_move_line.currency_id,
                                   account_move_line.amount_currency,
                                   account_move_line.matching_number,
                                   CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE ROUND(
                                       partial.amount * currency_table.rate, currency_table.precision
                                   ) END                                                                               AS debit, 
                                   CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE ROUND(
                                       partial.amount * currency_table.rate, currency_table.precision
                                   ) END                                                                               AS credit, 
                                   - sign(aml_with_partner.balance) * ROUND(
                                       partial.amount * currency_table.rate, currency_table.precision
                                   )                                                                                   AS balance, 
                                   account_move.name                                                                   AS move_name,
                                   account_move.move_type                                                              AS move_type,
                                   account.code                                                                        AS account_code,
                                   {account_name}                                                                      AS account_name,
                                   journal.code                                                                        AS journal_code,
                                   {journal_name}                                                                      AS journal_name,
                                   %s                                                                                  AS column_group_key,
                                   'indirectly_linked_aml'                                                             AS key
                               FROM {tables}
                                   LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id,
                                   account_partial_reconcile partial,
                                   account_move,
                                   account_move_line aml_with_partner,
                                   account_journal journal,
                                   account_account account
                               WHERE
                                   (account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id)
                                   AND account_move_line.partner_id IS NULL
                                   AND account_move.id = account_move_line.move_id
                                   AND (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                                   AND {indirectly_linked_aml_partner_clause}
                                   AND journal.id = account_move_line.journal_id
                                   AND account.id = account_move_line.account_id
                                   AND {where_clause}
                                   AND partial.max_date BETWEEN %s AND %s
                               ORDER BY account_move_line.date, account_move_line.id
                           ''')

        query = '(' + ') UNION ALL ('.join(queries) + ')'

        if offset:
            query += ' OFFSET %s '
            all_params.append(offset)

        if limit:
            query += ' LIMIT %s '
            all_params.append(limit)

        self._cr.execute(query, all_params)
        for aml_result in self._cr.dictfetchall():
            if aml_result['key'] == 'indirectly_linked_aml':

                # Append the line to the partner found through the reconciliation.
                if aml_result['partner_id'] in rslt:
                    rslt[aml_result['partner_id']].append(aml_result)

                # Balance it with an additional line in the Unknown Partner section but having reversed amounts.
                if None in rslt:
                    rslt[None].append({
                        **aml_result,
                        'debit': aml_result['credit'],
                        'credit': aml_result['debit'],
                        'balance': -aml_result['balance'],
                    })
            else:
                rslt[aml_result['partner_id']].append(aml_result)

        return rslt
