# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, Command, _
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot", )
    building_id = fields.Many2one('crm.building.state', 'Phase', )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', domain=[('is_project', '=', True)])
    installment_type = fields.Selection(
        [('dp', 'Down Payment'), ('unit', 'Unit'), ('main', 'Community'),
         ('utilities-electricity', 'Utilities(Electricity)'),
         ('utilities-water', 'Utilities(Water)'),
         ('utilities-stp', 'Utilities(STP)'),
         ('utilities-telecom', 'Utilities(Telecom)'),
         ('community', 'Community Deposit'), ('others', 'Others')], default='unit')
    partner_unit_ids = fields.Many2many('crm.unit.state', string='Units', compute='get_units')

    @api.depends('partner_id')
    def get_units(self):
        for rec in self:
            unit_ids = []
            if rec.partner_id and rec.move_type in ['out_invoice', 'out_refund']:
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
            for rec in self.invoice_line_ids:
                rec.analytic_distribution = {self.analytic_account_id.id: 100}
            for line in self.line_ids:
                line.analytic_distribution = {self.analytic_account_id.id: 100}
            return {'domain': {'building_id': [('analytic_account_id', '=', self.analytic_account_id.id)]}}
        else:
            return  {'domain':[]}

    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id:
            for rec in self.invoice_line_ids:
                rec.building_id = self.building_id and self.building_id.id or False
            for line in self.line_ids:
                line.building_id = self.building_id and self.building_id.id or False
            return {'domain': {'unit_id': [('building_id', '=', self.building_id.id)]}}
        else:
            return {'domain':[]}


    @api.onchange('unit_id')
    def onchange_unit_id(self):
        self.ensure_one()
        if self.unit_id:
            if self.unit_id.analytic_account_id:
                self.analytic_account_id = self.unit_id.analytic_account_id and self.unit_id.analytic_account_id.id or False
            if self.unit_id.building_id:
                self.building_id = self.unit_id.building_id and self.unit_id.building_id.id or False
            for rec in self.invoice_line_ids:
                rec.unit_id = self.unit_id and self.unit_id.id or False
            for line in self.line_ids:
                line.unit_id = self.unit_id and self.unit_id.id or False

    def write(self, values):
        res = super(AccountMove, self).write(values)
        for invoice in self:
            for rec in invoice.invoice_line_ids:
                # rec.analytic_account_id = self.analytic_account_id.id
                if invoice.unit_id:
                    rec.write({'unit_id': invoice.unit_id and invoice.unit_id.id})

                if invoice.building_id:
                    rec.write({'building_id': invoice.building_id and invoice.building_id.id})
                if invoice.analytic_account_id:
                    analytic_distribution = {}
                    if rec.analytic_distribution:
                        print('rec.analytic_distribution ===== ', rec.analytic_distribution)
                        analytic_distribution = rec.analytic_distribution
                        analytic_distribution[invoice.analytic_account_id.id] = 100
                    else:
                        analytic_distribution = {invoice.analytic_account_id.id: 100}
                    if rec.account_id:
                        rec.write(
                            {'analytic_distribution': analytic_distribution,
                             'building_id': invoice.building_id.id,
                             'unit_id': invoice.unit_id.id,
                             'installment_type': invoice.installment_type})

                    partner = invoice.partner_id
                    if rec.analytic_account_id:
                        for line in self.line_ids.filtered(
                                lambda line: line.account_id.account_type in ('asset_receivable', 'asset_payable')):
                            if line.account_id.account_type in ('asset_receivable', 'asset_payable'):
                                line_analytic_distribution = {}
                                if line.analytic_distribution:
                                    line_analytic_distribution = line.analytic_distribution
                                    line_analytic_distribution[invoice.analytic_account_id.id] = 100
                                else:
                                    line_analytic_distribution = {invoice.analytic_account_id.id: 100}
                                line.write({'analytic_distribution': line_analytic_distribution,
                                            'building_id': invoice.building_id.id, 'unit_id': invoice.unit_id.id,
                                            'installment_type': invoice.installment_type})
        return res

    @api.model
    def create(self, values):
        res = super(AccountMove, self).create(values)
        for line in res.line_ids:
            if line.move_id.unit_id:
                line.unit_id = line.move_id.unit_id.id
            if line.move_id.building_id:
                line.building_id = line.move_id.building_id.id
            if line.move_id.analytic_account_id:
                analytic_distribution = {}
                if line.analytic_distribution:
                    print('create lines rec.analytic_distribution ==== ', line.analytic_distribution)
                    analytic_distribution = line.analytic_distribution
                    print('create lines rec.move_id.analytic_account_id.id ==== ', line.move_id.analytic_account_id.id)
                    analytic_distribution[line.move_id.analytic_account_id.id] = 100
                else:
                    analytic_distribution = {line.move_id.analytic_account_id.id:100}
                line.analytic_distribution = analytic_distribution
            if line.move_id.installment_type:
                line.installment_type = line.move_id.installment_type

        for rec in res.invoice_line_ids:
            if rec.move_id.unit_id:
                rec.unit_id = rec.move_id.unit_id.id
            if rec.move_id.building_id:
                rec.building_id = rec.move_id.building_id.id
            if rec.move_id.analytic_account_id:
                analytic_distribution = {}
                if rec.analytic_distribution:
                    print('create inv lines rec.analytic_distribution ==== ', rec.analytic_distribution)
                    analytic_distribution = rec.analytic_distribution
                    print('create inv lines rec.move_id.analytic_account_id.id ==== ', rec.move_id.analytic_account_id.id)
                    analytic_distribution[rec.move_id.analytic_account_id.id] = 100
                else:
                    analytic_distribution = {rec.move_id.analytic_account_id.id:100}
                rec.analytic_distribution = analytic_distribution
            if rec.move_id.installment_type:
                rec.installment_type = rec.move_id.installment_type
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot", )
    building_id = fields.Many2one('crm.building.state', 'Phase', )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', domain=[('is_project', '=', True)])
    installment_type = fields.Selection(
        [('dp', 'Down Payment'), ('unit', 'Unit'), ('main', 'Community'),
         ('utilities-electricity', 'Utilities(Electricity)'),
         ('utilities-water', 'Utilities(Water)'),
         ('utilities-stp', 'Utilities(STP)'),
         ('utilities-telecom', 'Utilities(Telecom)'),
         ('community', 'Community Deposit'), ('others', 'Others')], default='unit')

    # @api.depends('display_type', 'company_id')
    # def _compute_account_id(self):
    #     super()._compute_account_id()
    #     for rec in self:
    #         rec_lines = self.filtered(
    #             lambda line: line.account_id.account_type == 'asset_receivable' and line.move_id.is_sale_document(
    #                 include_receipts=True))
    #         for line in rec_lines:
    #             if line.move_id.installment_type == 'unit' and line.company_id.installment_account_id:
    #                 line.account_id = line.company_id.installment_account_id and line.company_id.installment_account_id.id
    #
    #             if line.move_id.installment_type == 'main' and line.company_id.maintenance_check_account_id:
    #                 line.account_id = line.company_id.maintenance_check_account_id and line.company_id.maintenance_check_account_id.id
    #
    #             # Utilities Account
    #             if line.move_id.installment_type == 'utilities-electricity' and line.company_id.utilities_electric_check_account_id:
    #                 line.account_id = line.company_id.utilities_electric_check_account_id and line.company_id.utilities_electric_check_account_id.id
    #
    #             if line.move_id.installment_type == 'utilities-water' and line.company_id.utilities_water_check_account_id:
    #                 line.account_id = line.company_id.utilities_water_check_account_id and line.company_id.utilities_water_check_account_id.id
    #
    #             if line.move_id.installment_type == 'utilities-stp' and line.company_id.utilities_stp_check_account_id:
    #                 line.account_id = line.company_id.utilities_stp_check_account_id and line.company_id.utilities_stp_check_account_id.id
    #
    #             if line.move_id.installment_type == 'utilities-telecom' and line.company_id.utilities_telecom_check_account_id:
    #                 line.account_id = line.company_id.utilities_telecom_check_account_id and line.company_id.utilities_telecom_check_account_id.id
    #
    #             if line.move_id.installment_type == 'others' and line.company_id.others_check_account_id:
    #                 line.account_id = line.company_id.others_check_account_id and line.company_id.others_check_account_id.id
    #
    #             if line.move_id.installment_type == 'community' and line.company_id.community_check_account_id:
    #                 line.account_id = line.company_id.community_check_account_id and line.company_id.community_check_account_id.id

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
