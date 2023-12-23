# Copyright 2017 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def _stock_request_confirm_done_message_content(self, message_data):
        title = (
            _("Receipt confirmation %(picking_name)s for your Request %(request_name)s")
            % message_data
        )
        message = "<h3>%s</h3>" % title
        message += (
            _(
                "The following requested items from Stock Request %(request_name)s "
                "have now been received in %(location_name)s using Picking %(picking_name)s:"
            )
            % message_data
        )
        message += "<ul>"
        message += (
            _(
                "<li><b>%(product_name)s</b>: Transferred quantity %(product_qty)s"
                "%(product_uom)s</li>"
            )
            % message_data
        )
        message += "</ul>"
        return message

    def _prepare_message_data(self, ml, request, allocated_qty):
        return {
            "request_name": request.name,
            "picking_name": ml.picking_id.name,
            "product_name": ml.product_id.name_get()[0][1],
            "product_qty": allocated_qty,
            "product_uom": ml.product_uom_id.name,
            "location_name": ml.location_dest_id.name_get()[0][1],
        }


