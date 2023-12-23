# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models, Command


class PurchaseRequestAlternative(models.TransientModel):
    _inherit = "purchase.requisition.create.alternative"

    def _get_alternative_values(self):
        res = super()._get_alternative_values()
        vals = {
            'date_order': self.origin_po_id.date_order,
            'partner_id': self.partner_id.id,
            'user_id': self.origin_po_id.user_id.id,
            'dest_address_id': self.origin_po_id.dest_address_id.id,
            'origin': self.origin_po_id.origin,
            'note': self.origin_po_id.note,
            'type': self.origin_po_id.type.id,
        }
        list_id = []
        for rec in self.origin_po_id.order_line:
            order_line = rec
            po = rec.order_id
            print('=========== order_line.purchase_request_lines ============', order_line.purchase_request_lines)
            purchase_request_lines = order_line.purchase_request_lines
            request_id = purchase_request_lines.request_id.id
            print('============= request_id ===============', request_id)
        if self.copy_products and self.origin_po_id:
            vals['order_line'] = [Command.create({
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom.id,
                'display_type': line.display_type,
                'gl_account_id': line.gl_account_id.id,
                'purchase_request_lines': purchase_request_lines.ids,
                'name': line.name,
            }) for line in self.origin_po_id.order_line]
        return vals
