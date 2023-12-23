# -*- coding: utf-8 -*-
# from odoo import http


# class UpdateValuationLayerValue(http.Controller):
#     @http.route('/update_valuation_layer_value/update_valuation_layer_value/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/update_valuation_layer_value/update_valuation_layer_value/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('update_valuation_layer_value.listing', {
#             'root': '/update_valuation_layer_value/update_valuation_layer_value',
#             'objects': http.request.env['update_valuation_layer_value.update_valuation_layer_value'].search([]),
#         })

#     @http.route('/update_valuation_layer_value/update_valuation_layer_value/objects/<model("update_valuation_layer_value.update_valuation_layer_value"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('update_valuation_layer_value.object', {
#             'object': obj
#         })
