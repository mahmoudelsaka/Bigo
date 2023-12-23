# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning,UserError
import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Location')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    stock_location_report_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_report_users',
        'user_id',
        'location_id',
        'Stock Locations')

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Default Warehouse Operations')


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        self.check_user_location_rights()
        return super(stock_move, self)._action_done(cancel_backorder=cancel_backorder)
    # @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        for stock in self:
            if stock.state == 'draft':
               print('assssssssssss')
               return True
            user_locations = self.env.user.stock_location_ids
            
            if self.env.user.restrict_locations:
                _logger.info(f"stock.ref ============================================= {stock.reference}")
                _logger.info(f'user ================================= {self.env.user}')
                _logger.info(f'user locations ================================= {user_locations}')
                # message = _(
                #     'Invalid Location. You cannot process this move since you do '
                #     'not control the location "%s". '
                #     'Please contact your Adminstrator.')
                _logger.info(f'Source Location ================================= {stock.location_id.name} ====  {stock.location_id.id}')
                _logger.info(f'Destination Location ================================= {stock.location_dest_id.name} ==== {stock.location_dest_id.id}')
                if stock.location_id not in user_locations:
                    raise UserError(_('Invalid Source Location. You cannot process this move since you do not control the location "%s".Please contact your Adminstrator.') % self.location_id.name)

                    # raise UserError(message % self.location_id.name)

                if stock.location_dest_id not in user_locations:
                    raise UserError(_('Invalid Destenation Location. You cannot process this move since you do not control the location "%s".Please contact your Adminstrator.') % stock.location_dest_id.name)
            # stop


class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    to_usage = fields.Selection(related='location_id.usage')
    from_usage = fields.Selection(related='location_dest_id.usage')
