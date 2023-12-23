# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    installment_account_id = fields.Many2one(
        related='company_id.installment_account_id',
        readonly=False,
    )

    receivable_check_account_id = fields.Many2one(
        related='company_id.receivable_check_account_id',
        readonly=False,
    )
    old_receivable_check_account_id = fields.Many2one(related='company_id.old_receivable_check_account_id',
                                                      readonly=False)

    maintenance_check_account_id = fields.Many2one(
        related='company_id.maintenance_check_account_id',
        readonly=False,
    )

    # Utilities Accounts
    utilities_electric_check_account_id = fields.Many2one(
        related='company_id.utilities_electric_check_account_id',
        readonly=False,
    )

    utilities_water_check_account_id = fields.Many2one(
        related='company_id.utilities_water_check_account_id',
        readonly=False,
    )

    utilities_stp_check_account_id = fields.Many2one(
        related='company_id.utilities_stp_check_account_id',
        readonly=False,
    )

    utilities_telecom_check_account_id = fields.Many2one(
        related='company_id.utilities_telecom_check_account_id',
        readonly=False,
    )

    others_check_account_id = fields.Many2one(
        related='company_id.others_check_account_id',
        readonly=False,
    )

    community_check_account_id = fields.Many2one(
        related='company_id.community_check_account_id',
        readonly=False,
    )
