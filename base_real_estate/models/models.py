# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'

    # statement_id
    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot", readonly=False, )
    # related="statement_id.po_ro_id.unit_id")
    building_id = fields.Many2one('crm.building.state', 'Phase', readonly=False, )
    # related="statement_id.po_ro_id.building_id")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', domain=[('is_project', '=', True)],
                                          # related="statement_id.po_ro_id.analytic_account_id",
                                          readonly=False)

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
            self.analytic_account_id = self.building_id.analytic_account_id and self.building_id.analytic_account_id.id
            return {'domain': {'unit_id': [('building_id', '=', self.building_id.id)]}}
        else:
            return {'domain': []}

    def _prepare_move_line_default_vals(self, counterpart_account_id=None):
        data = super()._prepare_move_line_default_vals(counterpart_account_id=counterpart_account_id)
        for rec in data:
            if self.unit_id:
                rec['unit_id'] = self.unit_id and self.unit_id.id or False
            if self.building_id:
                rec['building_id'] = self.building_id and self.building_id.id or False
            if self.analytic_account_id:
                analytic_distribution = {}
                if 'analytic_distribution' in rec:
                    analytic_distribution = rec['analytic_distribution']
                else:
                    analytic_distribution = {self.analytic_account_id.id: 100}
                rec['analytic_distribution'] = analytic_distribution
        return data
