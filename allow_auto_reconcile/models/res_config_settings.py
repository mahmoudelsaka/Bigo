# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Company(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_auto_reconcile = fields.Boolean('Auto Reconcile (Invoices)', related='company_id.invoice_auto_reconcile', readonly=False)
    entry_auto_reconcile = fields.Boolean('Auto Reconcile (Entries)', related='company_id.entry_auto_reconcile', readonly=False)
