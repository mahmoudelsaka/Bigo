# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from dateutil.relativedelta import relativedelta

from odoo import models, api, fields, _, Command
from odoo.tools import format_date
from odoo.exceptions import UserError


class MulticurrencyRevaluationWizard(models.TransientModel):
    _inherit = 'account.multicurrency.revaluation.wizard'

    @api.depends('expense_provision_account_id', 'income_provision_account_id', 'date', 'journal_id')
    def _compute_preview_data(self):
        preview_columns = [
            {'field': 'account_id', 'label': _("Account")},
            {'field': 'partner_id', 'label': _("Partner")},
            {'field': 'unit_id', 'label': _("Plot")},
            {'field': 'building_id', 'label': _("Phase")},
            {'field': 'name', 'label': _("Label")},
            {'field': 'debit', 'label': _("Debit"), 'class': 'text-end text-nowrap'},
            {'field': 'credit', 'label': _("Credit"), 'class': 'text-end text-nowrap'},
        ]
        for record in self:
            preview_vals = [self.env['account.move']._move_dict_to_preview_vals(
                self._get_move_vals(),
                record.company_id.currency_id)
            ]
            record.preview_data = json.dumps({
                'groups_vals': preview_vals,
                'options': {
                    'columns': preview_columns,
                },
            })

    @api.model
    def _get_move_vals(self):
        def _get_model_id(parsed_line, selected_model):
            for dummy, parsed_res_model, parsed_res_id in parsed_line:
                if parsed_res_model == selected_model:
                    return parsed_res_id

        def _get_adjustment_balance(line):
            for column in line.get('columns'):
                if column.get('expression_label') == 'adjustment':
                    return column.get('no_format')

        report = self.env.ref('account_reports.multicurrency_revaluation_report')
        print('report.line_ids ========== ', report.line_ids)
        included_line_id = report.line_ids.filtered(lambda l: l.code == 'multicurrency_included').id
        generic_included_line_id = report._get_generic_line_id('account.report.line', included_line_id)
        options = {**self._context['multicurrency_revaluation_report_options'], 'unfold_all': False}
        report_lines = report._get_lines(options)
        move_lines = []

        for report_line in report._get_unfolded_lines(report_lines, generic_included_line_id):
            print('report_line ============= ', report_line)
            parsed_line_id = report._parse_line_id(report_line.get('id'))
            print('parsed_line_id =============== ', parsed_line_id[-1][-1])

            balance = _get_adjustment_balance(report_line)
            # print('balance ============ ', balance)
            # parsed_line_id[-1][-2] corresponds to res_model of the current line
            if (
                    parsed_line_id[-1][-2] == 'account.move.line'
                    and not self.env.company.currency_id.is_zero(balance)
            ):
                move_line_id = False
                if parsed_line_id[-1][-1] != 0:
                    move_line_id = self.env['account.move.line'].browse(parsed_line_id[-1][-1])


                account_id = _get_model_id(parsed_line_id, 'account.account')
                currency_id = _get_model_id(parsed_line_id, 'res.currency')
                # print('balance2 ============ ', balance)

                move_lines.append(Command.create({
                    'name': _(
                        "Provision for %(for_cur)s (1 %(comp_cur)s = %(rate)s %(for_cur)s)",
                        for_cur=self.env['res.currency'].browse(currency_id).display_name,
                        comp_cur=self.env.company.currency_id.display_name,
                        rate=options['currency_rates'][str(currency_id)]['rate']
                    ),
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': 0,
                    'currency_id': currency_id,
                    'account_id': account_id,
                    'unit_id': move_line_id.unit_id.id if move_line_id and move_line_id.unit_id else False,
                    'building_id': move_line_id.building_id.id if move_line_id and move_line_id.building_id else False,
                    'partner_id': move_line_id.partner_id.id if move_line_id and move_line_id.partner_id else False,
                    # 'date_maturity': move_line_id.date_maturity

                }))
                if balance < 0:
                    move_line_name = _("Expense Provision for %s",
                                       self.env['res.currency'].browse(currency_id).display_name)
                else:
                    move_line_name = _("Income Provision for %s",
                                       self.env['res.currency'].browse(currency_id).display_name)

                # print('balance3 ============ ', balance)
                move_lines.append(Command.create({
                    'name': move_line_name,
                    'debit': -balance if balance < 0 else 0,
                    'credit': balance if balance > 0 else 0,
                    'amount_currency': 0,
                    'currency_id': currency_id,
                    'account_id': self.expense_provision_account_id.id if balance < 0 else self.income_provision_account_id.id,
                    'unit_id': move_line_id.unit_id.id if move_line_id and move_line_id.unit_id else False,
                    'building_id': move_line_id.building_id.id if move_line_id and move_line_id.building_id else False,
                    'partner_id': move_line_id.partner_id.id if move_line_id and move_line_id.partner_id else False,
                    # 'date_maturity': move_line_id.date_maturity
                }))
        print('move_lines ================= ', move_lines)

        return {
            'ref': _("Foreign currencies adjustment entry as of %s", format_date(self.env, self.date)),
            'journal_id': self.journal_id.id,
            'date': self.date,
            'line_ids': move_lines,
        }
