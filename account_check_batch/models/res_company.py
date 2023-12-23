# -*- coding: utf-8 -*-

from odoo import models,fields,api


class ResCompany(models.Model):
    _inherit = 'res.company'

    installment_account_id = fields.Many2one(
        'account.account',
        'Check Installment Account',
        # help='Rejection Checks account, for eg. "Rejected Checks"',
    )
    receivable_check_account_id = fields.Many2one(
        'account.account',
        'Check Receivable Account',
        # help='Deferred Checks account, for eg. "Deferred Checks"',
    )

    old_receivable_check_account_id = fields.Many2one(
        'account.account',
        'Check Receivable (Old)',
        # help='Deferred Checks account, for eg. "Deferred Checks"',
    )

    maintenance_check_account_id = fields.Many2one(
        'account.account',
        'Maintenance Account',
        # help='Rejection Checks account, for eg. "Rejected Checks"',
    )

    utilities_electric_check_account_id = fields.Many2one(
        'account.account',
        'Utilities(Electric)',
    )

    utilities_water_check_account_id = fields.Many2one(
        'account.account',
        'Utilities(Water)',
    )
    utilities_stp_check_account_id = fields.Many2one(
        'account.account',
        'Utilities(STP)',
    )
    utilities_telecom_check_account_id = fields.Many2one(
        'account.account',
        'Utilities(Telecom)',
    )

    others_check_account_id = fields.Many2one(
        'account.account',
        'Others Account',
        # help='Rejection Checks account, for eg. "Rejected Checks"',
    )

    community_check_account_id = fields.Many2one(
        'account.account',
        'Community Account',
        # help='Rejection Checks account, for eg. "Rejected Checks"',
    )

    # def _get_check_account(self, type):
    #     res = super(ResCompany, self)._get_check_account(type)
    #
    #     if type == 'holding':
    #         account = self.holding_check_account_id
    #     elif type == 'rejected':
    #         account = self.rejected_check_account_id
    #     elif type == 'deferred':
    #         account = self.deferred_check_account_id
    #     else:
    #         raise UserError(_("Type %s not implemented!"))
    #     if not account:
    #         account = payment.journal_id.default_account_id.id
    #     return account