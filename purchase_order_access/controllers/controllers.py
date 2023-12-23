# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseOrderAccess(http.Controller):
#     @http.route('/purchase_order_access/purchase_order_access', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_order_access/purchase_order_access/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_order_access.listing', {
#             'root': '/purchase_order_access/purchase_order_access',
#             'objects': http.request.env['purchase_order_access.purchase_order_access'].search([]),
#         })

#     @http.route('/purchase_order_access/purchase_order_access/objects/<model("purchase_order_access.purchase_order_access"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_order_access.object', {
#             'object': obj
#         })
