# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountBookkeeperAccess(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super(AccountBookkeeperAccess, self).action_post()
        print('=========== THIS IS THE ACTION POST ==========')
        user_group = self.env.user.has_group('account.group_account_manager')
        print('============== user group ==============', user_group)
        if not user_group:
            raise ValidationError(_("You are not authorized to confirm this payment."))
        return res
