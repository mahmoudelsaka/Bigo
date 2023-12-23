# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError

from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_debit_account_id = fields.Many2one(
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]")
    payment_credit_account_id = fields.Many2one(
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]")
    suspense_account_id = fields.Many2one(
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                                 ('account_type', 'not in', ('receivable', 'payable'))]")
    default_account_id = fields.Many2one(

        domain="[('deprecated', '=', False), ('company_id', '=', company_id),"
               "('account_type', 'not in', ('receivable', 'payable'))]")


class AccountCheck(models.Model):
    _inherit = 'account.check'

    # installment = fields.Boolean('Installment', default=False, tracking=True, readonly=True,
    #                              states={'draft': [('readonly', False)]}, )
    # adv_pay = fields.Boolean('Advanced Payment', default=True, tracking=True, readonly=True,
    #                          states={'draft': [('readonly', False)]}, )
    installment_type = fields.Selection(selection=[('unit', 'Unit'), ('main', 'Community'), ('dp', 'Down Payment'),
                                                   ('utilities-electricity', 'Utilities(Electricity)'),
                                                   ('utilities-water', 'Utilities(Water)'),
                                                   ('utilities-stp', 'Utilities(STP)'),
                                                   ('utilities-telecom', 'Utilities(Telecom)'),
                                                   ('community', 'Community Deposit'), ('others', 'Others')],
                                        string='Type', readonly=True,
                                        states={'draft': [('readonly', False)]}, default='unit')

    # transfer_account_id = fields.Many2one(comodel_name="account.account", string="Transfer Account", required=False, )
    # reject_account_id = fields.Many2one(comodel_name="account.account", string="Reject Account", required=False, )

    @api.onchange('installment')
    def onchange_installment(self):
        if self.installment:
            self.adv_pay = False

    @api.onchange('adv_pay')
    def onchange_adv_pay(self):
        if self.adv_pay:
            self.installment = False

    @api.constrains('type', 'owner_name', 'bank_id', )
    def _check_unique(self):
        for rec in self:
            if rec.type == 'issue_check':
                same_checks = self.search([
                    ('checkbook_id', '=', rec.checkbook_id.id),
                    ('type', '=', rec.type),
                    ('number', '=', rec.number),
                ])
                same_checks -= self
                if same_checks:
                    raise ValidationError(_(
                        'Check Number (%s) must be unique per Checkbook!\n'
                        '* Check ids: %s') % (
                                              rec.name, same_checks.ids))
            # elif self.type == 'third_check':
            #     # agregamos condicion de company ya que un cheque de terceros
            #     # se puede pasar entre distintas cias
            #     same_checks = self.search([
            #         ('company_id', '=', rec.company_id.id),
            #         ('bank_id', '=', rec.bank_id.id),
            #         # ('owner_name', '=', rec.owner_name),
            #         ('type', '=', rec.type),
            #         ('number', '=', rec.number),
            #         ('installment_type', 'in', ['unit', 'main'])
            #     ])
            #     same_checks -= self
            #     if same_checks:
            #         raise ValidationError(_(
            #             'Check Number (%s) must be unique per Owner and Bank!'
            #             '\n* Check ids: %s') % (
            #                                   rec.name, same_checks.ids))
        return True

    def create_down_payment_entries(self, journal, ref, partner_id, amount, credit_account):
        for rec in self:
            currency = False
            debit = 0.0
            credit = 0.0
            amount_currency = 0.0
            default_company_currency = self.env.user.company_id.currency_id
            if rec.currency_id.id != default_company_currency.id:
                debit, credit = self.convert_amount_currency_to_company_currency(rec, amount)
                print('debit ========== credit =============== ', debit, credit)
                currency = rec.currency_id and rec.currency_id.id
                amount_currency = amount
            else:
                debit = amount
                credit = amount
            move_data = {
                'journal_id': journal.id,
                'ref': ref,
                'date': rec.payment_date,
                'move_type': 'entry',
                'rejected_check_id': rec.id,
                'line_ids': [
                    (0, 0, {
                        'name': ref,
                        'date_maturity': rec.payment_date,
                        'partner_id': partner_id.id,
                        'debit': debit,
                        'credit': 0.0,
                        'currency_id': currency,
                        'amount_currency': amount_currency,
                        'account_id': rec.company_id.installment_account_id and rec.company_id.installment_account_id.id,
                        'analytic_account_id': rec.analytic_account_id and rec.analytic_account_id.id or False,
                        'building_id': rec.building_id and rec.building_id.id or False,
                        'unit_id': rec.unit_id and rec.unit_id.id or False,
                        'installment_type': rec.installment_type,
                    }),
                    (0, 0, {
                        'name': ref,
                        'date_maturity': rec.payment_date,
                        'partner_id': partner_id.id,
                        'debit': 0.0,
                        'credit': credit,
                        'currency_id': currency,
                        'amount_currency': -amount_currency,
                        'account_id': credit_account.id,
                        'analytic_account_id': rec.analytic_account_id and rec.analytic_account_id.id or False,
                        'building_id': rec.building_id and rec.building_id.id or False,
                        'unit_id': rec.unit_id and rec.unit_id.id or False,
                        'installment_type': rec.installment_type,
                    }),
                ],
            }
            print('move_data ', move_data)

            move_id = self.env['account.move'].create(move_data)
            move_id.action_post()
            print('gates = moooooooooooove_id ', move_id)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    check_batch_id = fields.Many2one('account.check.batch')
    installment_type = fields.Selection(selection=[('unit', 'Unit'), ('main', 'Community'), ('dp', 'Down Payment'),
                                                   ('utilities-electricity', 'Utilities(Electricity)'),
                                                   ('utilities-water', 'Utilities(Water)'),
                                                   ('utilities-stp', 'Utilities(STP)'),
                                                   ('utilities-telecom', 'Utilities(Telecom)'),
                                                   ('community', 'Community Deposit'), ('others', 'Others')],
                                   string='Type',
                                   default='unit')

    def check_vals(self):
        res = super(AccountPayment, self).check_vals()
        installment_type = self.installment_type
        if self.installment_type == 'unit':
            installment_type = 'unit'
        res['installment_type'] = installment_type
        return res


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    installment_type = fields.Selection(selection=[('unit', 'Unit'), ('main', 'Community'), ('dp', 'Down Payment'),
                                                   ('utilities-electricity', 'Utilities(Electricity)'),
                                                   ('utilities-water', 'Utilities(Water)'),
                                                   ('utilities-stp', 'Utilities(STP)'),
                                                   ('utilities-telecom', 'Utilities(Telecom)'),
                                                   ('community', 'Community Deposit'), ('others', 'Others')],
                                   string='Type',
                                   default='unit')
