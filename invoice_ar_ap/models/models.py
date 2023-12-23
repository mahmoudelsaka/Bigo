# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError, AccessError


class AccountAccount(models.Model):
    _inherit = 'account.account'
    installment_type = fields.Selection(
        [('dp', 'Down Payment'), ('unit', 'Unit'), ('main', 'Community'),
         ('utilities-electricity', 'Utilities(Electricity)'),
         ('utilities-water', 'Utilities(Water)'),
         ('utilities-stp', 'Utilities(STP)'),
         ('utilities-telecom', 'Utilities(Telecom)'),
         ('community', 'Community Deposit'), ('others', 'Others')], default='unit')


class AccountMove(models.Model):
    _inherit = 'account.move'

    ar_ap_account_id = fields.Many2one('account.account',
                                       domain=[('account_type', 'in', ('asset_receivable', 'liability_payable'))])

    @api.onchange('ar_ap_account_id')
    def onchange_ar_ap_account_id(self):
        for rec in self:
            if rec.ar_ap_account_id:
                for line in rec.line_ids:
                    if line.account_id.account_type in ['asset_receivable', 'liability_payable']:
                        line.account_id = rec.ar_ap_account_id and rec.ar_ap_account_id.id
                rec.installment_type = rec.ar_ap_account_id.installment_type

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self = self.with_company(self.journal_id.company_id)
        warning = {}
        if self.partner_id:
            rec_account = self.partner_id.property_account_receivable_id
            pay_account = self.partner_id.property_account_payable_id
            if self.move_type in ['out_invoice', 'out_refund']:
                self.ar_ap_account_id = self.partner_id.property_account_receivable_id and self.partner_id.property_account_receivable_id.id or False
                print('base_real_estate before ===== ')
                if self.installment_type == 'unit' and self.company_id.installment_account_id:
                    print('base_real_estate after ===== ')
                    self.ar_ap_account_id = self.company_id.installment_account_id and self.company_id.installment_account_id.id

                if self.installment_type == 'main' and self.company_id.maintenance_check_account_id:
                    self.ar_ap_account_id = self.company_id.maintenance_check_account_id and self.company_id.maintenance_check_account_id.id

                # Utilities Account
                if self.installment_type == 'utilities-electricity' and self.company_id.utilities_electric_check_account_id:
                    self.ar_ap_account_id = self.company_id.utilities_electric_check_account_id and self.company_id.utilities_electric_check_account_id.id

                if self.installment_type == 'utilities-water' and self.company_id.utilities_water_check_account_id:
                    self.ar_ap_account_id = self.company_id.utilities_water_check_account_id and self.company_id.utilities_water_check_account_id.id

                if self.installment_type == 'utilities-stp' and self.company_id.utilities_stp_check_account_id:
                    self.ar_ap_account_id = self.company_id.utilities_stp_check_account_id and self.company_id.utilities_stp_check_account_id.id

                if self.installment_type == 'utilities-telecom' and self.company_id.utilities_telecom_check_account_id:
                    self.ar_ap_account_id = self.company_id.utilities_telecom_check_account_id and self.company_id.utilities_telecom_check_account_id.id

                if self.installment_type == 'others' and self.company_id.others_check_account_id:
                    self.ar_ap_account_id = self.company_id.others_check_account_id and self.company_id.others_check_account_id.id

                if self.installment_type == 'community' and self.company_id.community_check_account_id:
                    self.ar_ap_account_id = self.company_id.community_check_account_id and self.company_id.community_check_account_id.id

                if self.ar_ap_account_id:
                    rec_account = self.ar_ap_account_id
            if self.move_type in ['in_invoice', 'in_refund']:
                self.ar_ap_account_id = self.partner_id.property_account_payable_id and self.partner_id.property_account_payable_id.id or False
                if self.ar_ap_account_id:
                    pay_account = self.ar_ap_account_id

            if not rec_account and not pay_account:
                action = self.env.ref('account.action_account_config')
                msg = _(
                    'Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
            p = self.partner_id
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn and p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s", p.name),
                    'message': p.invoice_warn_msg
                }
                if p.invoice_warn == 'block':
                    self.partner_id = False
                return {'warning': warning}


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
        super()._compute_account_id()
        for rec in self:
            rec_lines = self.filtered(
                lambda line: line.account_id.account_type == 'asset_receivable' and line.move_id.is_sale_document(
                    include_receipts=True))
            for line in rec_lines:
                print('ar_pr_account before ===== ')
                if line.move_id.ar_ap_account_id:
                    print('ar_pr_account after ===== ')
                    line.account_id = line.move_id.ar_ap_account_id and line.move_id.ar_ap_account_id.id
