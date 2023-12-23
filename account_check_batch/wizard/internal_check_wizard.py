from odoo import models, fields, api, _


class AccountPayementInternalCheck(models.TransientModel):
    _inherit = 'account.payment.internal.check'

    def create_installment_entries(self, journal1, ref1, rec, partner_id1, amount1, debit_account1, credit_account1):
        currency = False
        debit = 0.0
        credit = 0.0
        amount_currency = amount1
        default_company_currency = self.env.user.company_id.currency_id
        if rec.currency_id.id != default_company_currency.id:
            debit, credit = self.convert_amount_currency_to_company_currency(rec, amount1)
            print('debit ========== credit =============== ', debit, credit)
            currency = rec.currency_id and rec.currency_id.id
            # amount_currency = amount1
        else:
            debit = amount1
            credit = amount1
        move_data = {
            'journal_id': journal1,
            'ref': ref1,
            'date': self.date,
            'move_type': 'entry',
            'rejected_check_id': rec.id,
            'line_ids': [
                (0, 0, {
                    'name': ref1,
                    'date_maturity': rec.payment_date,
                    'partner_id': partner_id1,
                    'debit': debit,
                    'credit': 0.0,
                    'currency_id': currency,
                    'amount_currency': amount_currency,
                    'account_id': debit_account1,
                    'analytic_account_id': rec.analytic_account_id and rec.analytic_account_id.id or False,
                    'building_id': rec.building_id and rec.building_id.id or False,
                    'unit_id': rec.unit_id and rec.unit_id.id or False,
                    'installment_type': rec.installment_type,
                }),
                (0, 0, {
                    'name': ref1,
                    'date_maturity': rec.payment_date,
                    'partner_id': partner_id1,
                    'debit': 0.0,
                    'credit': credit,
                    'currency_id': currency,
                    'amount_currency': -amount_currency,
                    'account_id': credit_account1,
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
