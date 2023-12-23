# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    stock_request_id = fields.Many2one('stock.request', 'Stock Request')

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('stock_request_id')
        return distinct_fields

    def _get_source_document(self):
        res = super()._get_source_document()
        return self.stock_request_id.order_id or res

    def _assign_picking_post_process(self, new=False):
        super(StockMove, self)._assign_picking_post_process(new=new)
        if new:
            picking_id = self.mapped('picking_id')
            order_request_ids = self.mapped('stock_request_id.order_id')
            for stock_order_id in order_request_ids:
                picking_id.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': picking_id, 'origin': stock_order_id},
                    subtype_id=self.env.ref('mail.mt_note').id)

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        res = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description)
        account_id = debit_account_id
        if self.picking_id and self.picking_id.gl_account:
            account_id = self.picking_id.gl_account.id
        if 'debit_line_vals' in res:
            if 'account_id' in res['debit_line_vals']:
                res['debit_line_vals']['account_id'] = account_id
        print("res['account_id']===", self.picking_id.gl_account.id)
        print("res['debit_line_vals']===", res['debit_line_vals'])
        return res

    def _get_all_related_sm(self, product):
        return super()._get_all_related_sm(product) | self.filtered(lambda m: m.stock_request_id.product_id == product)

    # @api.depends("allocation_ids")
    # def _compute_stock_request_ids(self):
    #     for rec in self:
    #         rec.stock_request_ids = rec.allocation_ids.mapped("order_id")

    # def _merge_moves_fields(self):
    #     res = super(StockMove, self)._merge_moves_fields()
    #     res["stock_request_ids"] = [(4, m.id) for m in self.mapped("stock_request_ids")]
    #     return res

    # @api.constrains("company_id")
    # def _check_company_stock_request(self):
    #     if any(
    #         self.env["stock.request.allocation"].search(
    #             [
    #                 ("company_id", "!=", rec.company_id.id),
    #                 ("stock_move_id", "=", rec.id),
    #             ],
    #             limit=1,
    #         )
    #         for rec in self
    #     ):
    #         raise ValidationError(
    #             _(
    #                 "The company of the stock request must match with "
    #                 "that of the location."
    #             )
    #         )
    #
    # def copy_data(self, default=None):
    #     if not default:
    #         default = {}
    #     if "allocation_ids" not in default:
    #         default["allocation_ids"] = []
    #     for alloc in self.allocation_ids:
    #         default["allocation_ids"].append(
    #             (
    #                 0,
    #                 0,
    #                 {
    #                     "stock_request_id": alloc.stock_request_id.id,
    #                     "requested_product_uom_qty": alloc.requested_product_uom_qty,
    #                     'order_id': alloc.order_id.id or False,
    #                 },
    #             )
    #         )
    #     return super(StockMove, self).copy_data(default)

    # def _action_cancel(self):
    #     """Apply sudo to prevent requests ACL errors if the user does not have
    #     permissions (example: productions)."""
    #     res = super()._action_cancel()
    #     self.mapped("stock_request_id").sudo().check_cancel()
    #     return res
    #
    # def _action_done(self, cancel_backorder=False):
    #     """Apply sudo to prevent requests ACL errors if the user does not have
    #     permissions (example: productions)."""
    #     res = super()._action_done(cancel_backorder=cancel_backorder)
    #     self.mapped("stock_request_id").sudo().check_done()
    #     return res
