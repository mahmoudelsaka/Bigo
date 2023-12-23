# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class StockRequest(models.Model):
    _name = "stock.request"
    _description = "Stock Request"
    _inherit = "stock.request.abstract"
    _order = "id desc"

    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @staticmethod
    def _get_expected_date():
        return fields.Datetime.now()

    name = fields.Char(states={"draft": [("readonly", False)]})
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("approve", "Approved"),
            ("open", "In progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        copy=False,
        default="draft",
        index=True,
        readonly=True,
        tracking=True,
    )
    requested_by = fields.Many2one(
        "res.users",
        required=True,
        tracking=True,
        default=lambda s: s._get_default_requested_by(),
    )
    expected_date = fields.Datetime(
        index=True,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Date when you expect to receive the goods.",
    )
    picking_policy = fields.Selection(
        [
            ("direct", "Receive each product when available"),
            ("one", "Receive all products at once"),
        ],
        string="Shipping Policy",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="direct",
    )
    move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name='stock_request_id',
        string="Stock Moves",
        readonly=True,
    )
    picking_ids = fields.One2many(
        "stock.picking",
        'stock_request_order_id',
        string="Pickings",
        readonly=True,
    )
    qty_in_progress = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity cancelled",
    )
    picking_count = fields.Integer(
        string="Delivery Orders",
        # compute="_compute_picking_ids",
        readonly=True,
    )

    order_id = fields.Many2one("stock.request.order", readonly=True)
    warehouse_id = fields.Many2one(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    location_id = fields.Many2one(
        states={"draft": [("readonly", False)]}, readonly=True,
        related='order_id.location_id', store=1
    )
    product_id = fields.Many2one(states={"draft": [("readonly", False)]}, readonly=True)
    product_uom_id = fields.Many2one(
        states={"draft": [("readonly", False)]},
    )
    product_uom_qty = fields.Float(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    procurement_group_id = fields.Many2one(
        states={"draft": [("readonly", False)]}, readonly=True
    )
    product_on_hand = fields.Integer('On Hand')

    company_id = fields.Many2one(states={"draft": [("readonly", False)]}, readonly=True)
    route_id = fields.Many2one(states={"draft": [("readonly", False)]}, readonly=True)

    _sql_constraints = [
        ("name_uniq", "unique(name, company_id)", "Stock Request name must be unique")
    ]

    def _prepare_stock_move_vals(self):
        vals = {
            'name': (self.product_id.display_name or '')[:2000],
            'product_id': self.product_id and self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'location_id': self.env['stock.rule'].sudo().search([('route_id', '=', self.route_id.id)], limit=1).location_src_id.id,
            'location_dest_id': self.location_id and self.location_id.id,
            'state': 'draft',
            'company_id': self.company_id.id,
            'stock_request_id': self.id,
            'origin': self.order_id.name,
            'description_picking': self.product_id.description_pickingin or self.name,
            'warehouse_id': self.order_id.warehouse_id.id,
            'product_uom': self.product_uom_id.id,
            'price_unit': self.product_id.standard_price,
        }
        return vals

    @api.onchange('product_id')
    def _compute_product_on_hand(self):
        for rec in self:
            if rec.product_id:
                stock_quanty = rec.product_id.stock_quant_ids
                quant_on_hand = 0.0
                for sq in stock_quanty:
                    if sq.location_id.usage == 'internal':
                        quant_on_hand += sq.quantity
                if quant_on_hand:
                    self.product_on_hand = quant_on_hand
                else:
                    self.product_on_hand = 0.0

    @api.depends(
        "move_ids",
        "move_ids.state",
        "move_ids.move_line_ids",
        "move_ids.move_line_ids.qty_done",
    )
    def _compute_qty(self):
        for request in self:
            incoming_qty = 0.0
            other_qty = 0.0
            for allocation in request.move_ids:
                if allocation.picking_code == "incoming":
                    incoming_qty += allocation.quantity_done
                else:
                    other_qty += allocation.quantity_done
            done_qty = abs(other_qty - incoming_qty)
            open_qty = sum(request.move_ids.mapped("quantity_done"))
            uom = request.product_id.uom_id
            request.qty_done = uom._compute_quantity(done_qty, request.product_uom_id)
            request.qty_in_progress = uom._compute_quantity(
                open_qty, request.product_uom_id
            )
            request.qty_cancelled = (
                max(
                    0,
                    uom._compute_quantity(
                        request.product_qty - done_qty - open_qty,
                        request.product_uom_id,
                    ),
                )
                if request.move_ids
                else 0
            )

    @api.constrains("order_id", "requested_by")
    def check_order_requested_by(self):
        if self.order_id and self.order_id.requested_by != self.requested_by:
            raise ValidationError(_("Requested by must be equal to the order"))

    @api.constrains("order_id", "warehouse_id")
    def check_order_warehouse_id(self):
        if self.order_id and self.order_id.warehouse_id != self.warehouse_id:
            raise ValidationError(_("Warehouse must be equal to the order"))

    @api.constrains("order_id", "location_id")
    def check_order_location(self):
        if self.order_id and self.order_id.location_id != self.location_id:
            raise ValidationError(_("Location must be equal to the order"))

    @api.constrains("order_id", "procurement_group_id")
    def check_order_procurement_group(self):
        if (
                self.order_id
                and self.order_id.procurement_group_id != self.procurement_group_id
        ):
            raise ValidationError(_("Procurement group must be equal to the order"))

    @api.constrains("order_id", "company_id")
    def check_order_company(self):
        if self.order_id and self.order_id.company_id != self.company_id:
            raise ValidationError(_("Company must be equal to the order"))

    @api.constrains("order_id", "expected_date")
    def check_order_expected_date(self):
        if self.order_id and self.order_id.expected_date != self.expected_date:
            raise ValidationError(_("Expected date must be equal to the order"))

    @api.constrains("order_id", "picking_policy")
    def check_order_picking_policy(self):
        if self.order_id and self.order_id.picking_policy != self.picking_policy:
            raise ValidationError(_("The picking policy must be equal to the order"))

    def action_approved(self):
        print('============ TEST !@# ============')
        self.write({"state": "approve"})
        return True

    def action_to_approved(self):
        print('============ TEST !@# ============')
        self.write({"state": "to_approve"})
        return True

    def _action_confirm(self):
        # self._action_launch_procurement_rule()
        self.write({"state": "open"})

    def action_confirm(self):
        self._action_confirm()
        return True

    def action_draft(self):
        self.write({"state": "draft"})
        return True

    def action_cancel(self):
        self.sudo().mapped("move_ids")._action_cancel()
        self.write({"state": "cancel"})
        return True

    def action_done(self):
        self.write({"state": "done"})
        return True

    def check_cancel(self):
        for request in self:
            if request._check_cancel_allocation():
                request.write({"state": "cancel"})

    def check_done(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for request in self:
            allocated_qty = sum(request.move_ids.mapped("quantity_done"))
            qty_done = request.product_id.uom_id._compute_quantity(
                allocated_qty, request.product_uom_id
            )
            if (
                    float_compare(
                        qty_done, request.product_uom_qty, precision_digits=precision
                    )
                    >= 0
            ):
                request.action_done()
            elif request._check_cancel_allocation():
                # If qty_done=0 and qty_cancelled>0 it's cancelled
                request.write({"state": "cancel"})
        return True

    def _check_cancel_allocation(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        self.ensure_one()
        return (
                self.move_ids
                and float_compare(self.qty_cancelled, 0, precision_digits=precision) > 0
        )

    def _prepare_procurement_values(self, group_id=False):

        """Prepare specific key for moves or other components that
        will be created from a procurement rule
        coming from a stock request. This method could be override
        in order to add other custom key that could be used in
        move/po creation.
        """
        return {
            "date_planned": self.expected_date,
            "warehouse_id": self.warehouse_id,
            'partner_id': self.order_id.requested_partner_id.id or False,
            # "stock_request_allocation_ids": self.id,
            "group_id": group_id or self.procurement_group_id.id or False,
            "route_ids": self.route_id,
            "stock_request_id": self.id,
            'company_id': self.order_id.company_id,
        }

    def _prepare_procurement_group_vals(self):
        return {
            'name': self.order_id.name,
            'move_type': self.order_id.picking_policy,
            'stock_request_order_id': self.order_id.id,
            'partner_id': self.order_id.requested_partner_id.id,
        }

    def _skip_procurement(self):
        skip = self.state not in ["draft", 'to_approve', 'approve'] or self.product_id.type not in ("consu", "product")
        print('skip ==================== ', skip)
        return skip

    def _get_procurement_group(self):
        return self.order_id.procurement_group_id


    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom
        fields genrated by a
        stock request. procurement group will launch '_run_move',
        '_run_buy' or '_run_manufacture'
        depending on the stock request product rule.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        errors = []
        for request in self:
            if request._skip_procurement():
                continue
            qty = 0.0
            for move in request.move_ids.filtered(lambda r: r.state != "cancel"):
                qty += move.product_qty

            if float_compare(qty, request.product_qty, precision_digits=precision) >= 0:
                continue

            group_id = request._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(request._prepare_procurement_group_vals())
                request.order_id.procurement_group_id = group_id


            values = request._prepare_procurement_values(
                group_id=request.procurement_group_id
            )
            product_qty = request.product_uom_qty - qty
            print('============= values ============', values)
            try:
                procurements = []
                procurements.append(
                    self.env["procurement.group"].Procurement(
                        request.product_id,
                        request.product_uom_qty,
                        request.product_uom_id,
                        request.location_id,
                        request.name,
                        request.name,
                        self.env.company,
                        values,
                    )
                )
                print('============== procurements ==========', procurements)
                x = self.env["procurement.group"].run(procurements)
                print('============ x ==============', x)
                orders = self.mapped('order_id')
                print('orders ======== ', orders)
                for order in orders:
                    pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
                    print('pickings_to_confirm ====== ', pickings_to_confirm)
                    if pickings_to_confirm:
                        # Trigger the Scheduler for Pickings
                        pickings_to_confirm.action_confirm()
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError("\n".join(errors))
        return True

    def action_view_transfer(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        pickings = self.mapped("picking_ids")
        if len(pickings) > 1:
            action["domain"] = [("id", "in", pickings.ids)]
        elif pickings:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = pickings.id
        return action

    @api.model
    def create(self, vals):
        upd_vals = vals.copy()
        if upd_vals.get("name", "/") == "/":
            upd_vals["name"] = self.env["ir.sequence"].next_by_code("stock.request")
        if "order_id" in upd_vals:
            order_id = self.env["stock.request.order"].browse(upd_vals["order_id"])
            upd_vals["expected_date"] = order_id.expected_date
        else:
            upd_vals["expected_date"] = self._get_expected_date()
        return super().create(upd_vals)

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft"):
            raise UserError(_("Only requests on draft state can be unlinked"))
        return super(StockRequest, self).unlink()
