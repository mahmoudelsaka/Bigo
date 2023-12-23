# -*- coding: utf-8 -*-
# from odoo import http


# class RtAnaylaticReceviable(http.Controller):
#     @http.route('/rt_anaylatic_receviable/rt_anaylatic_receviable', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_anaylatic_receviable/rt_anaylatic_receviable/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_anaylatic_receviable.listing', {
#             'root': '/rt_anaylatic_receviable/rt_anaylatic_receviable',
#             'objects': http.request.env['rt_anaylatic_receviable.rt_anaylatic_receviable'].search([]),
#         })

#     @http.route('/rt_anaylatic_receviable/rt_anaylatic_receviable/objects/<model("rt_anaylatic_receviable.rt_anaylatic_receviable"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_anaylatic_receviable.object', {
#             'object': obj
#         })
