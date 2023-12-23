# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class purchase_order_access(models.Model):
#     _name = 'purchase_order_access.purchase_order_access'
#     _description = 'purchase_order_access.purchase_order_access'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
