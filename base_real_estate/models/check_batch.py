# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AccountCheckBatchLine(models.Model):
    _inherit = 'account.check.batch.line'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot")
    building_id = fields.Many2one('crm.building.state', 'Phase', readonly=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', readonly=False, domain=[('is_project', '=', True)])

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            unit_ids = []
            if self.partner_id.unit_line_ids:
                for line in self.partner_id.unit_line_ids:
                    unit_ids.append(line.unit_id.id)
            return {'domain': {'unit_id': [('id', 'in', unit_ids)]}}

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        if self.analytic_account_id:
            return {'domain': {'building_id': [('analytic_account_id', '=', self.analytic_account_id.id)]}}
        else:
            return {'domain': {'building_id': []}}

    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id:
            return {'domain': {'unit_id': [('building_id', '=', self.building_id.id)]}}
        else:
            return {'domain': {'unit_id': []}}

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        self.ensure_one()
        if self.unit_id:
            if self.unit_id.analytic_account_id:
                self.analytic_account_id = self.unit_id.analytic_account_id and self.unit_id.analytic_account_id.id or False
            if self.unit_id.building_id:
                self.building_id = self.unit_id.building_id and self.unit_id.building_id.id or False


class AccountCheckBatch(models.Model):
    _inherit = 'account.check.batch'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot")
    building_id = fields.Many2one('crm.building.state', 'Phase',
                                  readonly=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project',domain=[('is_project', '=', True)],
                                          readonly=False)

    partner_unit_ids = fields.Many2many('crm.unit.state', string='Plots', compute='get_units')

    @api.depends('partner_id')
    def get_units(self):
        for rec in self:
            unit_ids = []
            if rec.partner_id:
                print('partner exist')
                if rec.partner_id.unit_line_ids:
                    for line in rec.partner_id.unit_line_ids:
                        unit_ids.append(line.unit_id.id)
            else:
                print('partner doesn\'t exist ======= ')
                for unit in self.env['crm.unit.state'].sudo().search([]):
                    unit_ids.append(unit.id)
            rec.partner_unit_ids = unit_ids

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

    def _prepare_check_val(self, amount):
        res = super()._prepare_check_val(amount=amount)
        res['unit_id'] = self.unit_id and self.unit_id.id or False
        res['building_id'] = self.building_id and self.building_id.id or False
        res['analytic_account_id'] = self.analytic_account_id and self.analytic_account_id.id or False

        return res

    def generate_check_number(self):
        if self.start:
            number = self.start
            for line in self.check_batch_line:
                if line.payment_type in ['unit', 'main']:
                    line.check_no = number
                    line.check_name = number
                    number += 1
                if line.payment_type == 'dp':
                    line.check_no = 0
                    line.check_name = line.unit_id.name + '-' + line.building_id.name + '-' + line.analytic_account_id.name + '/' + str(
                        line.check_payment_date)

    def payment_vals(self, line):
        res = super(AccountCheckBatch, self).payment_vals(line)
        if line.unit_id:
            res['unit_id'] = line.unit_id and line.unit_id.id or False
        if line.building_id:
            res['building_id'] = line.building_id and line.building_id.id or False
        if line.analytic_account_id:
            res['analytic_account_id'] = line.analytic_account_id and line.analytic_account_id.id or False
        return res

    def create_down_payment_check(self, line):
        res = super(AccountCheckBatch, self).create_down_payment_check(line)
        if line.unit_id:
            res['unit_id'] = line.unit_id and line.unit_id.id or False
        if line.building_id:
            res['building_id'] = line.building_id and line.building_id.id or False
        if line.analytic_account_id:
            res['analytic_account_id'] = line.analytic_account_id and line.analytic_account_id.id or False
        return res
