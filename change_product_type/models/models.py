# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, check_barcode_encoding
from odoo.addons.stock.models.product import ProductTemplate


class ProductTemp(ProductTemplate):
    _inherit = 'product.template'

    @api.onchange('type')
    def _onchange_type(self):
        # Return a warning when trying to change the product type
        res = super(ProductTemplate, self)._onchange_type()
        # if self.ids and self.product_variant_ids.ids and self.env['stock.move.line'].sudo().search_count([
        #     ('product_id', 'in', self.product_variant_ids.ids), ('state', '!=', 'cancel')
        # ]):
        #     res['warning'] = {
        #         'title': _('Warning!'),
        #         'message': _(
        #             'This product has been used in at least one inventory movement. '
        #             'It is not advised to change the Product Type since it can lead to inconsistencies. '
        #             'A better solution could be to archive the product and create a new one instead.'
        #         )
        #     }
        return res

    def write(self, vals):
        print('vals ========= ', vals)
        self._sanitize_vals(vals)
        if 'company_id' in vals and vals['company_id']:
            products_changing_company = self.filtered(lambda product: product.company_id.id != vals['company_id'])
            if products_changing_company:
                move = self.env['stock.move'].sudo().search([
                    ('product_id', 'in', products_changing_company.product_variant_ids.ids),
                    ('company_id', 'not in', [vals['company_id'], False]),
                ], order=None, limit=1)
                if move:
                    raise UserError(
                        _("This product's company cannot be changed as long as there are stock moves of it belonging to another company."))

                # Forbid changing a product's company when quant(s) exist in another company.
                quant = self.env['stock.quant'].sudo().search([
                    ('product_id', 'in', products_changing_company.product_variant_ids.ids),
                    ('company_id', 'not in', [vals['company_id'], False]),
                    ('quantity', '!=', 0),
                ], order=None, limit=1)
                if quant:
                    raise UserError(
                        _("This product's company cannot be changed as long as there are quantities of it belonging to another company."))

        if 'uom_id' in vals:
            new_uom = self.env['uom.uom'].browse(vals['uom_id'])
            updated = self.filtered(lambda template: template.uom_id != new_uom)
            done_moves = self.env['stock.move'].sudo().search(
                [('product_id', 'in', updated.with_context(active_test=False).mapped('product_variant_ids').ids)],
                limit=1)
            if done_moves:
                raise UserError(
                    _("You cannot change the unit of measure as there are already stock moves for this product. If you want to change the unit of measure, you should rather archive this product and create a new one."))
        if 'type' in vals and vals['type'] != 'product' and sum(self.mapped('nbr_reordering_rules')) != 0:
            raise UserError(
                _('You still have some active reordering rules on this product. Please archive or delete them first.'))
        if any('type' in vals and vals['type'] != prod_tmpl.type for prod_tmpl in self):
            existing_done_move_lines = self.env['stock.move.line'].sudo().search([
                ('product_id', 'in', self.mapped('product_variant_ids').ids),
                ('state', '=', 'done'),
            ], limit=1)
            # if existing_done_move_lines:
            #     raise UserError(_("You can not change the type of a product that was already used."))
            existing_reserved_move_lines = self.env['stock.move.line'].search([
                ('product_id', 'in', self.mapped('product_variant_ids').ids),
                ('state', 'in', ['partially_available', 'assigned']),
            ])
            if existing_reserved_move_lines:
                raise UserError(
                    _("You can not change the type of a product that is currently reserved on a stock move. If you need to change the type, you should first unreserve the stock move."))
        if 'type' in vals and vals['type'] != 'product' and any(
                p.type == 'product' and not float_is_zero(p.qty_available, precision_rounding=p.uom_id.rounding) for p
                in self):
            raise UserError(_("Available quantity should be set to zero before changing type"))
        return super(ProductTemplate, self).write(vals)
