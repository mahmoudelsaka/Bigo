# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class rt_share_user/opt/odoo_16/custom_addons/(models.Model):
#     _name = 'rt_share_user/opt/odoo_16/custom_addons/.rt_share_user/opt/odoo_16/custom_addons/'
#     _description = 'rt_share_user/opt/odoo_16/custom_addons/.rt_share_user/opt/odoo_16/custom_addons/'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
