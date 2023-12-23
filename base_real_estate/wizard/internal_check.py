from odoo import models


class AccountPaymentInternalCheck(models.TransientModel):
    _inherit = 'account.payment.internal.check'

    def prepare_move_vals(self, journal, ref, rec, partner_id, amount, debit_account, credit_account):
        res = super(AccountPaymentInternalCheck, self).prepare_move_vals(journal, ref, rec, partner_id, amount,
                                                                         debit_account, credit_account)
        res['unit_id'] = rec.unit_id and rec.unit_id.id or False
        res['building_id'] = rec.building_id and rec.building_id.id or False
        res['analytic_account_id'] = rec.analytic_account_id and rec.analytic_account_id.id or False
        return res

    def prepare_move_line_vals(self, ref, partner_id, amount, debit_account, credit_account, rec):
        res = super(AccountPaymentInternalCheck, self).prepare_move_line_vals(ref, partner_id, amount, debit_account,
                                                                              credit_account, rec)
        for line in res:
            if rec.unit_id:
                line[2]['unit_id'] = rec.unit_id and rec.unit_id.id or False
            if rec.building_id:
                line[2]['building_id'] = rec.building_id and rec.building_id.id or False
            if rec.analytic_account_id:
                line[2]['analytic_distribution'] = {rec.analytic_account_id.id: 100} or {}
        return res

    def create_move_entries(self, journal, ref, rec, partner_id, amount, debit_account, credit_account):
        move_id = super().create_move_entries(journal, ref, rec, partner_id, amount, debit_account, credit_account)
        if self.transfer_state in ['deposited', 'delivered'] \
                or self.holding_state in ['delivered', 'transfered']:
            print('xxxxxxxxxxxxxxxxxxxxxxxwwwwqqqqq')
            rec._reconcile_entries(move_id)
        # stop
        return move_id

    def create_internal_entries(self):
        check_ids = self.env['account.check']
        for rec in check_ids.browse(self.env.context['active_ids']):
            if self.transfer_state in ['deposited'] or self.holding_state == 'deposited':
                rec.create_collected_cashed_entries()
        return super(AccountPaymentInternalCheck, self).create_internal_entries()
