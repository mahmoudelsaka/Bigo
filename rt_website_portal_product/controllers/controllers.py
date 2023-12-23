# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PortalProducts(http.Controller):
    @http.route('/products', website=True, auth="public")
    def product_portal(self, **kw):
        products = request.env['product.product'].sudo().search([])
        vals = []
        # stock_location_ids
        user = request.env.user
        stock_location_ids = user.stock_location_ids
        print('========== the user stock stock_location_ids =========', stock_location_ids)
        for prod in products:
            stock_quanty = prod.stock_quant_ids
            quant_on_hand = 0.0
            quant_ava = 0.0
            if stock_location_ids:
                for sq in stock_quanty:
                    if sq.location_id in stock_location_ids:
                        if sq.location_id.usage == 'internal':
                            quant_on_hand += sq.quantity
                            quant_ava += sq.available_quantity
            else:
                for sq in stock_quanty:
                    if sq.location_id.usage == 'internal':
                        quant_on_hand += sq.quantity
                        quant_ava += sq.available_quantity
            val = {
                'product': prod,
                'on_hand': quant_on_hand,
                'ava_quantity': quant_ava
            }
            vals.append(val)
        return request.render("rt_website_portal_product.product_portal", {
            'products': vals
        })

    @http.route('/search/product', website=True, auth="public")
    def search_product_portal(self, **kw):
        name = str(kw['product_name'])
        products = request.env['product.product'].sudo().search(
            ['|', ('name', 'like', name), ('default_code', 'like', name)])

        vals = []
        # stock_location_ids
        user = request.env.user
        stock_location_ids = user.stock_location_ids
        print('========== the user stock stock_location_ids =========', stock_location_ids)
        for prod in products:
            stock_quanty = prod.stock_quant_ids
            quant_on_hand = 0.0
            quant_ava = 0.0
            if stock_location_ids:
                for sq in stock_quanty:
                    if sq.location_id in stock_location_ids:
                        if sq.location_id.usage == 'internal':
                            quant_on_hand += sq.quantity
                            quant_ava += sq.available_quantity
            else:
                for sq in stock_quanty:
                    if sq.location_id.usage == 'internal':
                        quant_on_hand += sq.quantity
                        quant_ava += sq.available_quantity
            val = {
                'product': prod,
                'on_hand': quant_on_hand,
                'ava_quantity': quant_ava
            }
            vals.append(val)
        return request.render("rt_website_portal_product.product_portal", {
            'products': vals
        })
