# -*- coding: utf-8 -*-
# from odoo import http


# class RtCustomCurrenciesRate(http.Controller):
#     @http.route('/rt_custom_currencies_rate/rt_custom_currencies_rate', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_custom_currencies_rate/rt_custom_currencies_rate/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_custom_currencies_rate.listing', {
#             'root': '/rt_custom_currencies_rate/rt_custom_currencies_rate',
#             'objects': http.request.env['rt_custom_currencies_rate.rt_custom_currencies_rate'].search([]),
#         })

#     @http.route('/rt_custom_currencies_rate/rt_custom_currencies_rate/objects/<model("rt_custom_currencies_rate.rt_custom_currencies_rate"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_custom_currencies_rate.object', {
#             'object': obj
#         })
