# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot")
    building_id = fields.Many2one('crm.building.state', 'Phase')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', domain=[('is_project', '=', True)])

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            unit_ids = []
            if self.partner_id.unit_line_ids:
                for line in self.partner_id.unit_line_ids:
                    unit_ids.append(line.unit_id.id)
            return {'domain': {'unit_id': [('id', 'in', unit_ids)]}}

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        self.ensure_one()
        if self.unit_id:
            if self.unit_id.analytic_account_id:
                self.analytic_account_id = self.unit_id.analytic_account_id and self.unit_id.analytic_account_id.id or False
            if self.unit_id.building_id:
                self.building_id = self.unit_id.building_id and self.unit_id.building_id.id or False

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

    def check_vals(self):
        res = super(AccountPayment, self).check_vals()
        if self.unit_id:
            res['unit_id'] = self.unit_id and self.unit_id.id or False
        if self.building_id:
            res['building_id'] = self.building_id and self.building_id.id or False
        if self.analytic_account_id:
            res['analytic_account_id'] = self.analytic_account_id and self.analytic_account_id.id or False
        return res

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
        print('_prepare_move_line_default_vals === ', res)
        # if self.payment_method_code in ['delivered_third_check', 'received_third_check']:
        for rec in res:
            if self.unit_id:
                rec['unit_id'] = self.unit_id and self.unit_id.id or False
            if self.building_id:
                rec['building_id'] = self.building_id and self.building_id.id or False
            if self.analytic_account_id:
                rec['analytic_distribution'] = {self.analytic_account_id.id: 100}
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot")
    building_id = fields.Many2one('crm.building.state', 'Phase', )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project',
                                          related='unit_id.analytic_account_id', store=True)

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        res['unit_id'] = self.line_ids[0].unit_id.id or False
        res['building_id'] = self.line_ids[0].building_id.id or False
        res['analytic_account_id'] = self.line_ids[0].analytic_account_id.id or False
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result=batch_result)
        res['unit_id'] = batch_result['lines'][0].unit_id.id or False
        res['building_id'] = batch_result['lines'][0].building_id.id or False
        res['analytic_account_id'] = batch_result['lines'][0].analytic_account_id.id or False
        return res
