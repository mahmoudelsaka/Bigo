# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PartnerUnit(models.Model):
    _name = 'partner.unit.line'

    unit_id = fields.Many2one(comodel_name="crm.unit.state", string="Plot", required=True)
    code = fields.Char(related='unit_id.code')
    building_id = fields.Many2one(related='unit_id.building_id')
    analytic_account_id = fields.Many2one(related='unit_id.analytic_account_id')
    partner_id = fields.Many2one('res.partner', 'partner')
    move_id = fields.Many2one('account.move', 'Invoice')


class Partner(models.Model):
    _inherit = 'res.partner'

    unit_line_ids = fields.One2many('partner.unit.line', 'partner_id', 'Units')
