# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class AccountCheck(models.Model):
    _inherit = 'account.check'

    unit_id = fields.Many2one(comodel_name="crm.unit.state",
                              string="Plot", readonly=True,
                              states={'draft': [('readonly', False)]}, )
    building_id = fields.Many2one('crm.building.state', 'Phase', readonly=True,
                                  states={'draft': [('readonly', False)]}, )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project',
                                          domain=[('is_project', '=', True)],
                                          readonly=True,
                                          states={'draft': [('readonly', False)]},
                                          )

    is_old_check = fields.Boolean('Is Old Check?')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            unit_ids = []
            if self.partner_id.unit_line_ids:
                for line in self.partner_id.unit_line_ids:
                    unit_ids.append(line.unit_id.id)

            return {'domain': {'unit_id': [('id', 'in', unit_ids)]}}

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        if self.analytic_account_id:
            return {'domain': {'building_id': [('analytic_account_id', '=', self.analytic_account_id.id)]}}
        else:
            return {'domain': []}

    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id:
            return {'domain': {'unit_id': [('building_id', '=', self.building_id.id)]}}
        else:
            return {'domain': []}

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        self.ensure_one()
        if self.unit_id:
            if self.unit_id.analytic_account_id:
                self.analytic_account_id = self.unit_id.analytic_account_id and self.unit_id.analytic_account_id.id or False
            if self.unit_id.building_id:
                self.building_id = self.unit_id.building_id and self.unit_id.building_id.id or False

    # Covert Amount to EGP

    # Journal Entry Main Data
    def _prepare_account_move(self, journal, date, line_ids, ref, installment_type='unit'):
        self.ensure_one()
        move_data = {
            'journal_id': journal.id,
            'ref': ref,
            'date': date,
            'move_type': 'entry',
            'company_id': self.company_id.id,
            'rejected_check_id': self.id,
            'installment_type': installment_type,
            'line_ids': line_ids
        }
        return move_data

    # Journal Entry lines Data
    def _prepare_account_move_line(self, debit_account, credit_account, partner, amount, currency, due_date,
                                   amount_currency=0.0, installment_type='unit'):
        self.ensure_one()
        vals = []
        # Debit Line
        debit_line = {
            'name': self.name,
            'date_maturity': due_date,
            'partner_id': partner.id,
            'debit': round(amount, 2),
            'credit': 0.0,
            'currency_id': currency.id,
            'amount_currency': round(amount_currency, 2),
            'account_id': debit_account,
            'building_id': self.building_id and self.building_id.id or False,
            'unit_id': self.unit_id and self.unit_id.id or False,
            'installment_type': installment_type,
        }
        if self.analytic_account_id:
            debit_line['analytic_distribution'] = {self.analytic_account_id.id: 100}

        vals.append((0, 0, debit_line))
        credit_line = {
            'name': self.name,
            'date_maturity': due_date,
            'partner_id': partner.id,
            'debit': 0.0,
            'credit': round(amount, 2),
            'currency_id': currency.id,
            'amount_currency': round(-1 * amount_currency, 2),
            'account_id': credit_account,
            'building_id': self.building_id and self.building_id.id or False,
            'unit_id': self.unit_id and self.unit_id.id or False,
            'installment_type': installment_type,
        }
        if self.analytic_account_id:
            credit_line['analytic_distribution'] = {self.analytic_account_id.id: 100}
        vals.append((0, 0, credit_line))
        return vals

    def get_debit_account(self):
        debit_account = self.company_id.receivable_check_account_id and self.company_id.receivable_check_account_id.id
        if self.is_old_check:
            debit_account = self.company_id.old_receivable_check_account_id and self.company_id.old_receivable_check_account_id.id
        return debit_account

    def get_credit_account(self):
        credit_account = False
        if self.installment_type == 'main' and self.company_id.maintenance_check_account_id:
            credit_account = self.company_id.maintenance_check_account_id and self.company_id.maintenance_check_account_id.id

        # Utilities Account
        if self.installment_type == 'utilities-electricity' and self.company_id.utilities_electric_check_account_id:
            credit_account = self.company_id.utilities_electric_check_account_id and self.company_id.utilities_electric_check_account_id.id

        if self.installment_type == 'utilities-water' and self.company_id.utilities_water_check_account_id:
            credit_account = self.company_id.utilities_water_check_account_id and self.company_id.utilities_water_check_account_id.id

        if self.installment_type == 'utilities-stp' and self.company_id.utilities_stp_check_account_id:
            credit_account = self.company_id.utilities_stp_check_account_id and self.company_id.utilities_stp_check_account_id.id

        if self.installment_type == 'utilities-telecom' and self.company_id.utilities_telecom_check_account_id:
            credit_account = self.company_id.utilities_telecom_check_account_id and self.company_id.utilities_telecom_check_account_id.id

        if self.installment_type == 'community' and self.company_id.community_check_account_id:
            credit_account = self.company_id.community_check_account_id and self.company_id.community_check_account_id.id

        if self.installment_type == 'others' and self.company_id.others_check_account_id:
            credit_account = self.company_id.others_check_account_id and self.company_id.others_check_account_id.id

        if self.installment_type == 'unit' and self.company_id.installment_account_id:
            credit_account = self.company_id.installment_account_id and self.company_id.installment_account_id.id
        return credit_account

    def get_amount(self):
        amount = self.amount
        if self.currency_id.id != self.company_id.currency_id.id:
            amount = self.convert_amount_currency_to_company_currency(self.amount)
        return amount

    # Create Journal Entry if check status in [collected or cashed]
    def create_collected_cashed_entries(self):
        if self.installment_type != 'dp':
            if self.company_id:

                date = self.payment_date
                collected_entry_id = self.env['account.move'].sudo().search([('rejected_check_id', '=', self.id)],
                                                                            order='id desc', limit=1)

                is_collected = collected_entry_id.ref
                if is_collected:
                    _logger.info("********* Is Collected Entry Reference *********** %s" % is_collected)
                    _logger.info("********* Is Collected Value *********** %s" % is_collected.startswith("Deposited"))
                    if collected_entry_id and is_collected.startswith("Deposited"):
                        date = collected_entry_id.date

                debit_account = self.get_debit_account()
                credit_account = self.get_credit_account()
                amount_currency = self.amount
                installment_type = self.installment_type
                amount = self.get_amount()

                # Journal Items Values
                line_ids = self._prepare_account_move_line(debit_account, credit_account, self.partner_id, amount,
                                                           self.currency_id, date, amount_currency, installment_type)

                # Journal Entry values
                ref = 'Collected Check Number %s' % self.name,
                account_move_vals = self._prepare_account_move(self.journal_id, date, line_ids, ref, installment_type)

                _logger.info("********** Account Move Vals ********* %s" % account_move_vals)
                if debit_account and credit_account:
                    move_id = self.env['account.move'].create(account_move_vals)
                    move_id.action_post()
                    print('Collected-02 ====== move_id ', move_id.id)
                    move_id.env.cr.commit()

                    _logger.info("********* Collected Move-ID ******** %s" % move_id)
                    invoices = []
                    self._reconcile_auto_invoices(move_id)

    def _reconcile_auto_invoices(self, move_id):
        payment_type = self.installment_type
        # if self.installment_type == 'unit':
        #     payment_type = 'unit'
        invoices = self.env['account.move'].sudo().search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('partner_id', '=', self.partner_id.id),
            ('analytic_account_id', '=', self.analytic_account_id.id),
            ('building_id', '=', self.building_id.id),
            ('unit_id', '=', self.unit_id.id),
            ('company_id', '=', self.company_id.id),
            ('installment_type', '=', payment_type),
            ('amount_residual', '>', 0)
        ], order='invoice_date_due asc')
        _logger.info(f'invoices ======= {invoices}')
        for invoice in invoices:
            _logger.info(f'invoice ========== TBR ===== {invoice}')
            if invoice.state == 'posted':
                for line in move_id.line_ids:
                    if line.account_id.reconcile and not line.reconciled:
                        invoice.js_assign_outstanding_line(line.id)
                        print('====== invoice is reconciled ==== ')

    def _reconcile_entries(self, move_id):
        entries = self.env['account.move'].sudo().search([
            ('move_type', '=', 'entry'),
            # ('partner_id', '=', self.partner_id.id),
            ('rejected_check_id', '=', self.id),
            ('company_id', '=', self.company_id.id),
        ])
        _logger.info(f'entries ======= {entries}')
        for mv in entries:
            _logger.info(f'entries ========== TBR ===== {mv}')
            if mv.state == 'posted':
                for line in move_id.line_ids:
                    if line.account_id.reconcile and not line.reconciled:
                        mv.js_assign_outstanding_line(line.id)
                        _logger.info('====== entries is reconciled ==== ')
