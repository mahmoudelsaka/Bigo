# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

import re

TAG_RE = re.compile(r'<[^>]+>')


class RtPortalStockRequest(http.Controller):

    @http.route(['/sr/info/<int:id>'], website=True, auth="public")
    def get_po_info(self, id=None, **kw):
        stock_request = request.env['stock.request.order'].sudo().search([('id', '=', int(id))])
        lines = stock_request.stock_request_ids
        return http.request.render('rt_portal_stock_request.get_po_info', {
            'stock_request_id': stock_request,
            'lines': lines,
        })

    @http.route('/sr/orders', website=True, auth="public")
    def po_orders(self, **kw):
        user_id = request.env.user
        print('========== user id ===========', user_id)
        orders = request.env['stock.request.order'].sudo().search([('create_uid', '=', user_id.id)])
        return request.render("rt_portal_stock_request.sr_orders", {
            'orders': orders
        })

    @http.route('/create_sr_web_order', website=True, auth="user")
    def po_webform(self, **kw):
        location_id = int(request.env['ir.config_parameter'].sudo().get_param(
            'rt_portal_stock_request.location_id')),
        company_id = request.env.company.id
        warehouse = request.env['stock.warehouse'].sudo().search([('company_id', '=', company_id)])
        location_id = request.env['stock.location'].sudo().search([])
        account_id = request.env['account.account'].sudo().search([('is_request', '=', True)])
        return http.request.render('rt_portal_stock_request.create_sr_from_website', {
            'warehouse': warehouse,
            'location': location_id,
            'account_id': account_id,
        })

    @http.route(['/cancel/sr/<int:id>'], website=True, auth="public")
    def cancel_stock_request_order(self, id=None, **kw):
        print('=========== this is the cancel function ==========')
        print('=========== the id is =============', id)
        user_id = request.env.user
        if id:
            stock_request_order = request.env['stock.request.order'].sudo().search([('id', '=', int(id))])
            if stock_request_order:
                stock_request_order.write({
                    'state': 'cancel'
                })
                orders = request.env['stock.request.order'].sudo().search([('create_uid', '=', user_id.id)])
                return request.render("rt_portal_stock_request.sr_orders", {
                    'orders': orders
                })

    # ========= this is to submit stock request ============
    @http.route(['/submit_sr'], website=True, auth="user")
    def submit_br_request(self, **kw):
        id = int(kw['id'])
        if id:
            sr = request.env['stock.request.order'].sudo().search([('id', '=', id)])
            if sr.state != 'approve':
                sr.sudo().action_to_approved()

                lines = sr.stock_request_ids
                return http.request.render('rt_portal_stock_request.get_po_info', {
                    'stock_request_id': sr,
                    'lines': lines,
                })
        else:
            print('========= there is not id here ==============')

    @http.route(['/create/sr_web', '/create/sr_web/<int:sr_id>'], website=True, auth="user")
    def create_sr_webform(self, sr_id=None, **kw):
        print('============= kw =================', kw)
        company_id = request.env.company.id
        product = request.env['product.product'].sudo().search([])
        uom = request.env['uom.uom'].sudo().search([])
        route = request.env['stock.route'].sudo().search([('company_id', '=', company_id)])
        user = request.env.user
        user_partner_id = user.partner_id

        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        approve_id = employee.parent_id.user_id

        if sr_id != None:
            sr_rec = request.env['stock.request.order'].sudo().search([('id', '=', int(sr_id))])
            if sr_rec:
                return http.request.render('rt_portal_stock_request.add_lines', {
                    'id': sr_rec[0].id,
                    'name': sr_rec[0].name,
                    'warehouse_id': sr_rec[0].warehouse_id,
                    'location_id': sr_rec[0].location_id,
                    'product': product,
                    'uom': uom,
                    'route': route,
                    'company_id': company_id,
                    'sr_rec': sr_rec,
                })

        location_id = int(request.env['ir.config_parameter'].sudo().get_param(
            'rt_portal_stock_request.location_id')),
        print('========== location_id ============', location_id)
        if location_id:
            val = {
                'warehouse_id': int(kw['warehouse']),
                'location_id': location_id,
                'company_id': company_id,
                'gl_account': int(kw['account_id']),
                'type': 'portal',
                'description': kw['description'],
                'requested_partner_id': user_partner_id.id,
                'approver_by': approve_id.id if approve_id else False
            }

            sr = request.env['stock.request.order'].sudo().create(val)
            return http.request.render('rt_portal_stock_request.add_lines', {
                'id': sr.id,
                'name': sr.name,
                'warehouse_id': sr.warehouse_id,
                'location_id': sr.location_id,
                'company_id': company_id,
                'product': product,
                'uom': uom,
                'route': route,
                'sr_rec': sr,
            })

    @http.route('/create/sr_line', website=True, auth="user")
    def create_sr_line(self, **kw):

        id = int(kw['id'])
        product_id = int(kw['product'])
        # uom = int(kw['uom'])
        # route = int(kw['route'])
        product_qty = 0.0

        product = request.env['product.product'].sudo().search([('id', '=', product_id)])
        product_uom = product.uom_id
        if kw['quantity']:
            product_qty = float(kw['quantity'])
        sr = request.env['stock.request.order'].sudo().search([('id', '=', id)])
        location_id = sr.location_id
        product_cat = product.categ_id
        product_cat_route = product_cat.route_ids
        new_route = ''
        for rou in product_cat_route:
            if rou.name == location_id.name:
                new_route = rou

        if new_route:
            val_l = {
                'order_id': sr.id,
                'product_id': product_id,
                'product_uom_id': product_uom.id,
                'route_id': new_route.id,
                'product_uom_qty': product_qty,
                'location_id': sr.location_id.id,
            }
        else:
            val_l = {
                'order_id': sr.id,
                'product_id': product_id,
                'product_uom_id': product_uom.id,
                'route_id': 0.0,
                'product_uom_qty': product_qty,
                'location_id': sr.location_id.id,
            }

        srl = request.env['stock.request'].sudo().create(val_l)
        return request.redirect(f'/create/sr_web/{sr.id}')

    @http.route(['/edit/sr', '/edit/sr/<int:sr_id>'], website=True, auth="user")
    def edit_sr_webform(self, sr_id=None, **kw):
        sr_rec = request.env['stock.request.order'].sudo().search([('id', '=', int(sr_id))])
        print('============= sr rec ==============', sr_rec.description)
        company_id = request.env.company.id
        warehouse = request.env['stock.warehouse'].sudo().search([('company_id', '=', company_id)])
        location_id = request.env['stock.location'].sudo().search([])
        account_id = request.env['account.account'].sudo().search([('is_request', '=', True)])

        desc = sr_rec.description
        new_desc = TAG_RE.sub('', desc)

        return http.request.render('rt_portal_stock_request.edit_sr_from_website', {
            'warehouse': warehouse,
            'location': location_id,
            'account_id': account_id,
            'description': new_desc,
            'sr_id': sr_rec,
            'id': sr_rec.id,
        })

    @http.route('/edit/sr_web', website=True, auth="user")
    def edit_sr_web_form(self, sr_id=None, **kw):
        print('================ the value of kw is ==============', kw)
        id = int(kw['id'])
        warehouse_id = int(kw['warehouse'])
        location_id = int(kw['location'])
        account_id = int(kw['account_id'])
        description = kw['description']
        print('========== this is the description======', description)
        stock_request_obj = request.env['stock.request.order'].sudo().search([('id', '=', id)])
        sr = stock_request_obj.write({
            'warehouse_id': warehouse_id,
            'location_id': location_id,
            'gl_account': account_id,
            'description': description,
            'expected_date': kw['expected_date']
        })
        print('========= sr ===========', sr)
        company_id = request.env.company.id
        product = request.env['product.product'].sudo().search([])
        uom = request.env['uom.uom'].sudo().search([])
        route = request.env['stock.route'].sudo().search([('company_id', '=', company_id)])

        return http.request.render('rt_portal_stock_request.add_lines', {
            'id': stock_request_obj.id,
            'name': stock_request_obj.name,
            'warehouse_id': stock_request_obj.warehouse_id,
            'location_id': stock_request_obj.location_id,
            'product': product,
            'uom': uom,
            'route': route,
            'company_id': company_id,
            'sr_rec': stock_request_obj,
        })


class StockCustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        """Set the count as None"""

        if 'p_count' in counters:
            values['p_count'] = None
        return values

    @http.route('/product/stock/search', type='json', auth="user", website=True)
    def search_stock_product(self, **kw, ):
        """To get corresponding products"""
        print('=============== TEST ===============', kw)
        product = kw.get('name')
        if product:
            res = request.env['product.product'].sudo().search_read(
                [('name', 'ilike', product)], limit=100)
            return res
        else:
            res = request.env['product.product'].sudo().search_read([])
            return res
