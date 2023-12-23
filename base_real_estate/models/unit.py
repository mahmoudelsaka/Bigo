# -*- coding: utf-8 -*-

from odoo import models, fields, api

UNIT_TYPE = [('duplex', 'Duplex'), ('unit', 'Apartment'), ('basement', 'Basement'),
             ('villa', 'Villa'), ('studio', 'Studio'), ('chalet', 'Chalet'), ('twin-house', 'Twin House'),
             ('roof', 'Roof'), ('cov', 'Chill-out Villa'), ('palace', 'Palace'), ('ivilla', 'I-Villa'),
             ('town-villa', 'Townhouse'), ('grand-villa', 'Grand Villa'), ('penthouse', 'Penthouse')]


class Analytic(models.Model):
    _inherit = 'account.analytic.account'

    is_project = fields.Boolean('Is Projects?')

class CrmUnitState(models.Model):
    _name = 'crm.unit.state'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Unit"
    _order = "id desc"
    _check_company_auto = True

    # Main Fields
    state = fields.Selection(
        selection=[('free', 'Free'), ('reserved', 'Reserved'), ('contracted', 'Contracted')],
        default='free')
    name = fields.Char(string='Name', required=True, tracking=True,
                       )

    code = fields.Char(string='Code', required=True, tracking=True, )

    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', required=True, tracking=True, domain=[('is_project', '=', True)])

    building_id = fields.Many2one('crm.building.state', 'Phase', required=True, tracking=True, )
    # Unit Pricing
    unit_price = fields.Float('Unit Price', required=True, tracking=True, )

    club_price = fields.Float('Club Price', tracking=True, )

    garage_price = fields.Float('Garage Price',  tracking=True, )

    finishing_price = fields.Float('Finishing Price', tracking=True, )

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, )

    currency_id = fields.Many2one('res.currency', 'Currency')

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        if self.analytic_account_id:
            return {'domain': {'building_id': [('analytic_account_id', '=', self.analytic_account_id.id)]}}
        else:
            return {'domain': []}

    def name_get(self):
        res = []
        for unit in self:
            name = unit.name
            if unit.code:
                name = f'[{unit.code}] {name}'
            res.append((unit.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # name = name.replace(" ", "")
            domain = ['|', ('name', operator, name),
                      ('code', operator, name)
                      ]
            units = self.search(domain + args, limit=limit, )
            res = units.name_get()
            if limit:
                limit_rest = limit - len(units)
            else:
                limit_rest = limit
            if limit_rest or not limit:
                args += [('id', 'not in', units.ids)]
                res += super().name_search(
                    name, args=args, operator=operator, limit=limit_rest)
            return res
        return super().name_search(
            name, args=args, operator=operator, limit=limit
        )


class CrmBuildingState(models.Model):
    _name = 'crm.building.state'

    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Phases"
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char(string='Name', tracking=True)
    code = fields.Char(string='Code', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', tracking=True, domain=[('is_project', '=', True)])
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, tracking=True)
