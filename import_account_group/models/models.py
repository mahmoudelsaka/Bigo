# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Account(models.Model):
    _inherit = 'account.account'

    group_id = fields.Many2one(readonly=False)
