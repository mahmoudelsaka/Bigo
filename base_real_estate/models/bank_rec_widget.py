# -*- coding: utf-8 -*-

from odoo import models, fields, api,Command

class BankRecWidgetLine(models.Model):
    _inherit = 'bank.rec.widget.line'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Unit", compute='_compute_unit_building_id')
    building_id = fields.Many2one('crm.building.state', 'Building/Floor', compute='_compute_unit_building_id')


    @api.depends('wizard_id')
    def _compute_unit_building_id(self):
        for line in self:
            if line.flag in ('aml', 'new_aml'):
                line.unit_id = line.wizard_id.st_line_id.unit_id
                line.building_id = line.wizard_id.st_line_id.building_id
            elif line.flag in ('liquidity', 'auto_balance', 'manual', 'early_payment', 'tax_line'):
                line.unit_id = line.wizard_id.st_line_id.unit_id
                line.building_id = line.wizard_id.st_line_id.building_id
            else:
                line.unit_id = line.wizard_id.st_line_id.unit_id
                line.building_id = line.wizard_id.st_line_id.building_id


class AccountBankStatementLine(models.Model):
    _inherit = "bank.rec.widget"

    def button_validate(self, async_action=False):
        self.ensure_one()

        if self.state != 'valid':
            self.next_action_todo = {'type': 'move_to_next'}
            return

        partners = (self.line_ids.filtered(lambda x: x.flag != 'liquidity')).partner_id
        partner_id_to_set = partners.id if len(partners) == 1 else None

        # Prepare the lines to be created.
        to_reconcile = []
        line_ids_create_command_list = []
        aml_to_exchange_diff_vals = {}

        for i, line in enumerate(self.line_ids):
            if line.flag == 'exchange_diff':
                continue
            analytic_distribution = {}
            if line.analytic_distribution:
                analytic_distribution = line.analytic_distribution
                if self.st_line_id:
                    if self.st_line_id.analytic_account_id:
                        analytic_distribution[self.st_line_id.analytic_account_id.id] = 100

            amount_currency = line.amount_currency
            balance = line.balance
            if line.flag == 'new_aml':
                to_reconcile.append((i, line.source_aml_id.id))
                exchange_diff = self.line_ids \
                    .filtered(lambda x: x.flag == 'exchange_diff' and x.source_aml_id == line.source_aml_id)
                if exchange_diff:
                    aml_to_exchange_diff_vals[i] = {
                        'amount_residual': exchange_diff.balance,
                        'amount_residual_currency': exchange_diff.amount_currency
                    }
                    # Squash amounts of exchange diff into corresponding new_aml
                    amount_currency += exchange_diff.amount_currency
                    balance += exchange_diff.balance

            line_ids_create_command_list.append(Command.create({
                'name': line.name,
                'sequence': i,
                'account_id': line.account_id.id,
                'partner_id': partner_id_to_set if line.flag in ('liquidity', 'auto_balance') else line.partner_id.id,
                'currency_id': line.currency_id.id,
                'amount_currency': amount_currency,
                'balance': balance,
                'reconcile_model_id': line.reconcile_model_id.id,
                'analytic_distribution': analytic_distribution,
                'tax_repartition_line_id': line.tax_repartition_line_id.id,
                'tax_ids': [Command.set(line.tax_ids.ids)],
                'tax_tag_ids': [Command.set(line.tax_tag_ids.ids)],
                'group_tax_id': line.group_tax_id.id,
                'unit_id': self.st_line_id.unit_id and self.st_line_id.unit_id.id or False,
                'building_id': self.st_line_id.building_id and self.st_line_id.building_id.id or False,
            }))

        self.js_action_reconcile_st_line(
            self.st_line_id.id,
            {
                'command_list': line_ids_create_command_list,
                'to_reconcile': to_reconcile,
                'exchange_diff': aml_to_exchange_diff_vals,
                'partner_id': partner_id_to_set,
            },
        )
        self.next_action_todo = {'type': 'reconcile_st_line'}
