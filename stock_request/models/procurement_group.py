# Copyright (C) 2019 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"
    stock_request_order_id = fields.Many2one("stock.request.order", readonly=True)

