# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class rt_custom_currencies_rate(models.Model):
#     _name = 'rt_custom_currencies_rate.rt_custom_currencies_rate'
#     _description = 'rt_custom_currencies_rate.rt_custom_currencies_rate'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
