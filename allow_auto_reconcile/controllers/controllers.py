# -*- coding: utf-8 -*-
# from odoo import http


# class AllowAutoReconcile(http.Controller):
#     @http.route('/allow_auto_reconcile/allow_auto_reconcile', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/allow_auto_reconcile/allow_auto_reconcile/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('allow_auto_reconcile.listing', {
#             'root': '/allow_auto_reconcile/allow_auto_reconcile',
#             'objects': http.request.env['allow_auto_reconcile.allow_auto_reconcile'].search([]),
#         })

#     @http.route('/allow_auto_reconcile/allow_auto_reconcile/objects/<model("allow_auto_reconcile.allow_auto_reconcile"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('allow_auto_reconcile.object', {
#             'object': obj
#         })
