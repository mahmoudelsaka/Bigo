# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReceiptOrder(models.Model):
    _inherit = 'receipt.order'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot")
    building_id = fields.Many2one('crm.building.state', 'Phase', )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', domain=[('is_project', '=', True)])

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            unit_ids = []
            if self.partner_id.unit_line_ids:
                for line in self.partner_id.unit_line_ids:
                    unit_ids.append(line.unit_id.id)
            return {'domain': {'unit_id': [('id', 'in', unit_ids)]}}


    def get_statement_data(self, statement_id):
        res = super(ReceiptOrder, self).get_statement_data(statement_id=statement_id)
        if self.unit_id:
            res['unit_id'] = self.unit_id and self.unit_id.id or False
        if self.building_id:
            res['building_id'] = self.building_id and self.building_id.id or False
        if self.analytic_account_id:
            res['analytic_account_id'] = self.analytic_account_id and self.analytic_account_id.id or False
        print('PO/RO res ============== ', res)
        return res

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
