# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    date_expected = fields.Datetime(
        'Expected Date', default=fields.Datetime.now, index=True, required=True,
        states={'done': [('readonly', False)]},
        help="Scheduled date for the processing of this move")


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""
    _inherit = 'stock.valuation.layer'

    unit_cost = fields.Monetary('Unit Value', readonly=False)
    value = fields.Monetary('Total Value', readonly=False)
    product_id = fields.Many2one(readonly=False)
    remaining_qty = fields.Float(digits=0, readonly=False)
    remaining_value = fields.Monetary('Remaining Value', readonly=False)
    quantity = fields.Float('Quantity', digits=0, help='Quantity', readonly=False)
    create_date = fields.Datetime(readonly=False)
