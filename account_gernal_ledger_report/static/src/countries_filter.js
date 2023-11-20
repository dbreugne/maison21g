odoo.define('account_gernal_ledger_report.countries_filter', function (require) {
	var accountReportsWidget = require('account_reports.account_report');

	var core = require('web.core');
	var Context = require('web.Context');
	var AbstractAction = require('web.AbstractAction');
	var Dialog = require('web.Dialog');
	var datepicker = require('web.datepicker');
	var session = require('web.session');
	var field_utils = require('web.field_utils');
	var RelationalFields = require('web.relational_fields');
	var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
	var WarningDialog = require('web.CrashManager').WarningDialog;
	var Widget = require('web.Widget');

	var QWeb = core.qweb;
	var _t = core._t;

	var M2MFilters = Widget.extend(StandaloneFieldManagerMixin, {
    /**
     * @constructor
     * @param {Object} fields
     */
    init: function (parent, fields) {
        this._super.apply(this, arguments);
        StandaloneFieldManagerMixin.init.call(this);
        this.fields = fields;
        this.widgets = {};
    },
    /**
     * @override
     */
    willStart: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        _.each(this.fields, function (field, fieldName) {
            defs.push(self._makeM2MWidget(field, fieldName));
        });
        return Promise.all(defs);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        var $content = $(QWeb.render("m2mWidgetTable", {fields: this.fields}));
        self.$el.append($content);
        _.each(this.fields, function (field, fieldName) {
            self.widgets[fieldName].appendTo($content.find('#'+fieldName+'_field'));
        });
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * This method will be called whenever a field value has changed and has
     * been confirmed by the model.
     *
     * @private
     * @override
     * @returns {Promise}
     */
    _confirmChange: function () {
        var self = this;
        var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
        var data = {};
        _.each(this.fields, function (filter, fieldName) {
            data[fieldName] = self.widgets[fieldName].value.res_ids;
        });
        this.trigger_up('value_changed', data);
        return result;
    },
    /**
     * This method will create a record and initialize M2M widget.
     *
     * @private
     * @param {Object} fieldInfo
     * @param {string} fieldName
     * @returns {Promise}
     */
    _makeM2MWidget: function (fieldInfo, fieldName) {
        var self = this;
        var options = {};
        options[fieldName] = {
            options: {
                no_create_edit: true,
                no_create: true,
            }
        };
        return this.model.makeRecord(fieldInfo.modelName, [{
            fields: [{
                name: 'id',
                type: 'integer',
            }, {
                name: 'display_name',
                type: 'char',
            }],
            name: fieldName,
            relation: fieldInfo.modelName,
            type: 'many2many',
            value: fieldInfo.value,
        }], options).then(function (recordID) {
            self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                fieldName,
                self.model.get(recordID),
                {mode: 'edit',}
            );
            self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    },
	});



	accountReportsWidget.include({
		render_searchview_buttons: function() {

        var self = this;
        this._super();
        // if (this.report_options.country) {
            if (!this.M2MFilters_country) {
                var fields = {};
                // if ('country' in this.report_options) {
                    fields['country'] = {
                        label: _t('Country'),
                        modelName: 'res.country',
                    };
                // }
                if (!_.isEmpty(fields)) {
                    this.M2MFilters_country = new M2MFilters(this, fields);
                    this.M2MFilters_country.appendTo(this.$searchview_buttons.find('.account_countrym2m'));
                }
            } else {
                this.$searchview_buttons.find('.account_countrym2m').append(this.M2MFilters_country.$el);
            }
        // }
    },
    custom_events: {
        'value_changed': function(ev) {
             var self = this;
             self.report_options.partner_ids = ev.data.partner_ids;
             self.report_options.partner_categories = ev.data.partner_categories;
             self.report_options.analytic_accounts = ev.data.analytic_accounts;
             self.report_options.analytic_tags = ev.data.analytic_tags;
             self.report_options.country = ev.data.country;
             console.log("::::::::::::::::::::::::::",self.report_options.country)
             return self.reload().then(function () {
                 self.$searchview_buttons.find('.account_partner_filter').click();
                 self.$searchview_buttons.find('.account_analytic_filter').click();
                 if(ev.target.$el.parents().hasClass('account_countrym2m'))
                { self.$searchview_buttons.find('.account_country_filter').click();
                }
                 
             });
         },
    },
    
	})

});