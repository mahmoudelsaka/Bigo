# -*- coding: utf-8 -*-
# from odoo import http


# class BaseRealEstate(http.Controller):
#     @http.route('/base_real_estate/base_real_estate', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_real_estate/base_real_estate/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_real_estate.listing', {
#             'root': '/base_real_estate/base_real_estate',
#             'objects': http.request.env['base_real_estate.base_real_estate'].search([]),
#         })

#     @http.route('/base_real_estate/base_real_estate/objects/<model("base_real_estate.base_real_estate"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_real_estate.object', {
#             'object': obj
#         })
