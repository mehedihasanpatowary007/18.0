odoo.define('your_module.pos_patch', function(require) {
    "use strict";

    var models = require('point_of_sale.models');

    // Patch the Order prototype to ensure uid is included in sync data
    var _super_order_export = models.Order.prototype.export_as_JSON;
    models.Order.prototype.export_as_JSON = function() {
        var json = _super_order_export.call(this);
        // Ensure uid is always included
        if (this.uid) {
            json.uid = this.uid;
        }
        return json;
    };
});