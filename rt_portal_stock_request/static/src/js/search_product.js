odoo.define('rt_portal_stock_request.stock_portal_product_availability', function (require) {
    'use strict';
var publicStockWidget = require('web.public.widget');
var core = require('web.core');
var core = require('web.core');
var QWeb = core.qweb;
var ajax = require('web.ajax');


publicStockWidget.registry.SearchBarStock = publicStockWidget.Widget.extend({
    selector: '.o_stock_website_product_search',

    events: {
        'keyup #product_stock_name_input': '_product_stock_search',
    },
    init: function () {
            this._super.apply(this, arguments);
    },
    _product_stock_search: function (ev) {
        var product_name_val = $('#product_stock_name_input').val();
        console.log('============ TEST ==================')
        ajax.jsonRpc("/product/stock/search", 'call', {
                'name' : product_name_val
        }).then(function (res) {
            if (res != 'false'){
                 $('.product_stock_results_table').html(QWeb.render('productStockSearch',{'res':res}));
            }
        })
    }
    })
})


