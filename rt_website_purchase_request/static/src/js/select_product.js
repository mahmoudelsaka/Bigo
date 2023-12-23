odoo.define('rt_website_purchase_request.get_gl_account', function(require) {

    var rpc = require('web.rpc');

    $('.product_name_input').keyup(function(ev) {
        rpc.query({
            model: 'purchase.request',
            method: 'get_gl_account',
        }).then(function(result){
            $('.product_results_table').html(QWeb.render('productSearch',{'result':result}));
        });
    });

});