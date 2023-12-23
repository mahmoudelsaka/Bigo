# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockRequestUser(models.Model):
    _inherit = 'res.users'

    is_stock = fields.Boolean('Show Stock portal Menu')


class StockRequestConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="warehouse", store=True)
    location_id = fields.Many2one(comodel_name='stock.location', string="Location", store=True)

    def set_values(self):
        res = super(StockRequestConfiguration, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        location_id = self.location_id and self.location_id.id or False
        warehouse_id = self.warehouse_id and self.warehouse_id.id or False
        param.set_param('rt_portal_stock_request.location_id', location_id)
        param.set_param('rt_portal_stock_request.warehouse_id', warehouse_id)
        return res

    @api.model
    def get_values(self):
        res = super(StockRequestConfiguration, self).get_values()
        res.update(
            location_id=int(self.env['ir.config_parameter'].sudo().get_param(
                'rt_portal_stock_request.location_id')),
            warehouse_id=int(self.env['ir.config_parameter'].sudo().get_param(
                'rt_portal_stock_request.warehouse_id')),

        )
        print('=========== res ===========', res)
        return res


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    def change_childs(self):
        if not self._context.get("no_change_childs", False):
            for line in self.stock_request_ids:
                line.warehouse_id = self.warehouse_id
                line.location_id = self.location_id
                line.company_id = self.company_id
                line.picking_policy = self.picking_policy
                line.expected_date = self.expected_date
                line.requested_by = self.requested_by
                line.procurement_group_id = self.procurement_group_id

    @api.onchange("location_id")
    def onchange_location_id(self):
        if self.location_id:
            warehouse_id = int(self.env['ir.config_parameter'].sudo().get_param(
                'rt_portal_stock_request.warehouse_id')),
            if warehouse_id:
                self.warehouse_id = warehouse_id
            loc_wh = self.location_id.warehouse_id
            if loc_wh and self.warehouse_id != loc_wh:
                if warehouse_id:
                    self.warehouse_id = warehouse_id
                else:
                    self.warehouse_id = loc_wh
                self.with_context(no_change_childs=True).onchange_warehouse_id()
        self.change_childs()

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            # search with sudo because the user may not have permissions
            location_id = int(self.env['ir.config_parameter'].sudo().get_param(
                'rt_portal_stock_request.location_id')),
            if location_id:
                self.location_id = location_id
            loc_wh = self.location_id.warehouse_id
            if self.warehouse_id != loc_wh:
                location_id = int(self.env['ir.config_parameter'].sudo().get_param(
                    'rt_portal_stock_request.location_id')),
                if location_id:
                    self.location_id = location_id
                else:
                    self.location_id = self.warehouse_id.lot_stock_id
                self.with_context(no_change_childs=True).onchange_location_id()
            if self.warehouse_id.company_id != self.company_id:
                self.company_id = self.warehouse_id.company_id
                self.with_context(no_change_childs=True).onchange_company_id()
        self.change_childs()


class StockRequestPicking(models.Model):
    _inherit = 'stock.picking'

    description = fields.Html('Description')

    def write(self, vals):
        note = ''
        gl_account = 0.0
        for rec in self:
            if rec.stock_request_ids:
                for rec2 in rec.stock_request_ids:
                    note = rec2.order_id.description
                    gl_account = rec2.order_id.gl_account
        if note:
            vals['description'] = note
        if gl_account:
            vals['gl_account'] = gl_account
        return super(StockRequestPicking, self).write(vals)

    # def button_validate(self):
    #     res = super(StockRequestPicking, self).button_validate()
    #     note = ''
    #     for rec in self:
    #         gl_account_id = ''
    #         # if rec.stock_request_ids:
    #         #     for rec2 in rec.stock_request_ids:
    #         #         gl_account_id = rec2.order_id.gl_account
    #         #         note = rec2.order_id.description
    #         #         print('=========== the note is ==============', note)
    #         #         _logger.info(f'***** gl_account_id ****** {gl_account_id}')
    #
    #         if rec.gl_account:
    #             # for rec2 in rec.stock_request_ids:
    #             #     gl_account_id = rec2.order_id.gl_account
    #             #     note = rec2.order_id.description
    #             #     print('=========== the note is ==============', note)
    #             #     _logger.info(f'***** gl_account_id ****** {gl_account_id}')
    #             gl_account_id = rec.gl_account
    #
    #     account_id = self.move_ids.account_move_ids
    #     lines = account_id.invoice_line_ids
    #     for line in lines:
    #         if line.debit:
    #             _logger.info(f'***** gl_account_id ****** {gl_account_id}')
    #             if gl_account_id:
    #                 line.write({
    #                     'account_id': gl_account_id.id
    #                 })
    #     return res


class StockPortalRequest(models.Model):
    _inherit = 'stock.request'

    def remove_record(self, rec_product):
        self.env['stock.request'].sudo().search([('id', '=', int(rec_product))]).unlink()
        return True
