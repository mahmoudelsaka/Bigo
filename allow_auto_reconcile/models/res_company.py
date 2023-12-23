# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Company(models.Model):
    _inherit = 'res.company'

    invoice_auto_reconcile = fields.Boolean('Auto Reconcile (Invoices)')
    entry_auto_reconcile = fields.Boolean('Auto Reconcile (Entries)')
