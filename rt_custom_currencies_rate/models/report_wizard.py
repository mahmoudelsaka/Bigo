# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from odoo.tools import format_date


class RtCustomCurrenciesRate(models.TransientModel):
    _inherit = 'account.multicurrency.revaluation.wizard'

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
        included_line_id = report.line_ids.filtered(lambda l: l.code == 'multicurrency_included').id
        generic_included_line_id = report._get_generic_line_id('account.report.line', included_line_id)
        options = {**self._context['multicurrency_revaluation_report_options'], 'unfold_all': False}
        report_lines = report._get_lines(options)

        account_move = []
        for rec in report_lines:
            parsed_line_id = report._parse_line_id(rec.get('id'))
            account_id = _get_model_id(parsed_line_id, 'account.account')
            print('=============== account_id =============', account_id)
            if len(parsed_line_id) == 4:
                for acl in parsed_line_id:
                    if acl[1] == 'account.move.line':
                        acl = self.env['account.move.line'].sudo().search([('id', '=', acl[2])]).move_id
                        if acl.id not in account_move:
                            val = {
                                'account_move': acl,
                                'account_id': account_id,
                                'report_line': rec
                            }
                            account_move.append(val)
        print('============ account move ==========', account_move)
        print('============ account move ==========', len(account_move))
        flag = False
        move_lines = []
        for report_line in report._get_unfolded_lines(report_lines, generic_included_line_id):
            parsed_line_id = report._parse_line_id(report_line.get('id'))
            balance = _get_adjustment_balance(report_line)
            # parsed_line_id[-1][-2] corresponds to res_model of the current line
            if (
                    parsed_line_id[-1][-2] == 'account.account' and not self.env.company.currency_id.is_zero(balance)):
                flag = True
                account_id = _get_model_id(parsed_line_id, 'account.account')
                currency_id = _get_model_id(parsed_line_id, 'res.currency')
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
                }))
                if balance < 0:
                    move_line_name = _("Expense Provision for %s",
                                       self.env['res.currency'].browse(currency_id).display_name)
                else:
                    move_line_name = _("Income Provision for %s",
                                       self.env['res.currency'].browse(currency_id).display_name)
                move_lines.append(Command.create({
                    'name': move_line_name,
                    'debit': -balance if balance < 0 else 0,
                    'credit': balance if balance > 0 else 0,
                    'amount_currency': 0,
                    'currency_id': currency_id,
                    'account_id': self.expense_provision_account_id.id if balance < 0 else self.income_provision_account_id.id,
                }))
        if flag:
            for mov in account_move:
                print('============ mov =============', mov)
                account_move = mov['account_move']
                account_id = mov['account_id']
                report_line = mov['report_line']
                print('============= account move =============', account_move)
                print('============= account_id =============', account_id)
                print('============= report_line =============', report_line)
                unit_id = 0.0
                building_id = 0.0
                partner_id = 0.0
                if account_move:
                    if account_move.unit_id:
                        unit_id = account_move.unit_id
                    if account_move.building_id:
                        building_id = account_move.building_id
                    if account_move.partner_id:
                        partner_id = account_move.partner_id

                balance = _get_adjustment_balance(report_line)
                print('=============== balance =============', balance)

                if unit_id and building_id and partner_id:
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
                        'unit_id': unit_id.id,
                        'building_id': building_id.id,
                        'partner_id': partner_id.id,
                    }))
                    if balance < 0:
                        move_line_name = _("Expense Provision for %s",
                                           self.env['res.currency'].browse(currency_id).display_name)
                    else:
                        move_line_name = _("Income Provision for %s",
                                           self.env['res.currency'].browse(currency_id).display_name)
                    move_lines.append(Command.create({
                        'name': move_line_name,
                        'debit': -balance if balance < 0 else 0,
                        'credit': balance if balance > 0 else 0,
                        'amount_currency': 0,
                        'currency_id': currency_id,
                        'account_id': self.expense_provision_account_id.id if balance < 0 else self.income_provision_account_id.id,
                    }))
        print('============= move_lines 1111 ==============', move_lines)
        return {
            'ref': _("Foreign currencies adjustment entry as of %s", format_date(self.env, self.date)),
            'journal_id': self.journal_id.id,
            'date': self.date,
            'line_ids': move_lines,
        }

    def create_entries(self):
        self.ensure_one()
        move_vals = self._get_move_vals()
        if move_vals['line_ids']:
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            reverse_move = move._reverse_moves(default_values_list=[{
                'ref': _("Reversal of: %s", move.ref),
            }])
            reverse_move.date = self.reversal_date
            reverse_move.action_post()

            form = self.env.ref('account.view_move_form', False)
            ctx = self.env.context.copy()
            ctx.pop('id', '')
            return {
                'type': 'ir.actions.act_window',
                'res_model': "account.move",
                'res_id': move.id,
                'view_mode': "form",
                'view_id': form.id,
                'views': [(form.id, 'form')],
                'context': ctx,
            }
        raise UserError(_("No provision needed was found."))
