# -*- coding: utf-8 -*-
# from odoo import http


# class ChangeProductType(http.Controller):
#     @http.route('/change_product_type/change_product_type', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/change_product_type/change_product_type/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('change_product_type.listing', {
#             'root': '/change_product_type/change_product_type',
#             'objects': http.request.env['change_product_type.change_product_type'].search([]),
#         })

#     @http.route('/change_product_type/change_product_type/objects/<model("change_product_type.change_product_type"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('change_product_type.object', {
#             'object': obj
#         })
