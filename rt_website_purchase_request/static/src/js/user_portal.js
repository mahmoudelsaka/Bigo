odoo.define('rt_website_purchase_request.portal_operations', function(require) {

    var rpc = require('web.rpc');

    $('.fetch_user_customer').click(function(ev) {
        var recProduct = $(ev.target).data('rec_product');
        rpc.query({
            model: 'purchase.request.line',
            method: 'remove_record',
            args: ['', recProduct],
        }).then(function(result){
            location.reload();
        });
    });

});