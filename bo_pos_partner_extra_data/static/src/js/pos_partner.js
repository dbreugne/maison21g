odoo.define('bo_pos_partner_extra_data.pos_partner', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var _t = core._t;

var PosModelSuper = models.PosModel;

models.load_fields("res.partner", ["birthdate", "gender", "married", "children"]);

models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        var res = PosModelSuper.prototype.initialize.apply(this, arguments);
        this.genders = [{'code': 'female', 'name': _t('Female')},{'code': 'male', 'name': _t('Male')},{'code': 'unisex', 'name': _t('Unisex')}];
        this.married = [{'code': '', 'name': ''},{'code': 'yes', 'name': _t('Yes')}, {'code': 'no', 'name': _t('No')}];
        this.children =[{'code': '', 'name': ''},{'code': 'yes', 'name': _t('Yes')}, {'code': 'no', 'name': _t('No')}];
        return res;
    },
});

});