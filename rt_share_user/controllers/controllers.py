# -*- coding: utf-8 -*-
# from odoo import http


# class RtShareUser/opt/odoo16/customAddons/(http.Controller):
#     @http.route('/rt_share_user/opt/odoo_16/custom_addons//rt_share_user/opt/odoo_16/custom_addons/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_share_user/opt/odoo_16/custom_addons//rt_share_user/opt/odoo_16/custom_addons//objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_share_user/opt/odoo_16/custom_addons/.listing', {
#             'root': '/rt_share_user/opt/odoo_16/custom_addons//rt_share_user/opt/odoo_16/custom_addons/',
#             'objects': http.request.env['rt_share_user/opt/odoo_16/custom_addons/.rt_share_user/opt/odoo_16/custom_addons/'].search([]),
#         })

#     @http.route('/rt_share_user/opt/odoo_16/custom_addons//rt_share_user/opt/odoo_16/custom_addons//objects/<model("rt_share_user/opt/odoo_16/custom_addons/.rt_share_user/opt/odoo_16/custom_addons/"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_share_user/opt/odoo_16/custom_addons/.object', {
#             'object': obj
#         })
