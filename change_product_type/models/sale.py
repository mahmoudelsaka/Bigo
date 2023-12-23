# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.sale.models.product_product import ProductProduct
from odoo.addons.sale.models.product_template import ProductTemplate


class Template(ProductTemplate):
    _inherit = 'product.template'

    @api.onchange('type')
    def _onchange_type(self):
        res = super(Template, self)._onchange_type()
        # if self._origin and self.sales_count > 0:
        #     res['warning'] = {
        #         'title': _("Warning"),
        #         'message': _("You cannot change the product's type because it is already used in sales orders.")
        #     }
        return res


class Product(ProductProduct):
    _inherit = 'product.product'

    @api.onchange('type')
    def _onchange_type(self):
        res = super(Product, self)._onchange_type()
        # if self._origin and self.sales_count > 0:
        #     res['warning'] = {
        #         'title': _("Warning"),
        #         'message': _("You cannot change the product's type because it is already used in sales orders.")
        #     }
        return res
