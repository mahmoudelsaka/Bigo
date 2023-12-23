# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools.sql import column_exists, create_column

class StockPicking(models.Model):
    _inherit = "stock.picking"

    stock_request_ids = fields.One2many(
        comodel_name="stock.request",
        string="Stock Requests",
        compute="_compute_stock_request_ids",
    )
    stock_request_count = fields.Integer(
        "Stock Request #", compute="_compute_stock_request_ids"
    )

    gl_account = fields.Many2one(comodel_name='account.account', string="Gl Account", store=True)
    stock_request_order_id = fields.Many2one('stock.request.order', readonly=False)

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        self.stock_request_order_id.action_done()
        return res

    def _auto_init(self):
        """
        Create related field here, too slow
        when computing it afterwards through _compute_related.

        Since group_id.sale_id is created in this module,
        no need for an UPDATE statement.
        """
        if not column_exists(self.env.cr, 'stock_picking', 'stock_request_order_id'):
            create_column(self.env.cr, 'stock_picking', 'stock_request_order_id', 'int4')
        return super()._auto_init()

    @api.depends("move_ids")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.move_ids.mapped("stock_request_id")
            rec.stock_request_count = len(rec.stock_request_ids)

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_request.action_stock_request_form"
        )
        requests = self.mapped("stock_request_order_id").stock_request_ids
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action
