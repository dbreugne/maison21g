/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AccountTypeSelection } from "@account/components/account_type_selection/account_type_selection";

patch(AccountTypeSelection.prototype, {
    get hierarchyOptions() {
        const opts = this.options;
        console.log("66666666666666666666",opts)
        var data= [
            { name: _t('Balance Sheet') },
            { name: _t('Assets'), children: opts.filter(x => x[0] && x[0].startsWith('asset')) },
            { name: _t('Liabilities'), children: opts.filter(x => x[0] && x[0].startsWith('liability')) },
            { name: _t('Equity'), children: opts.filter(x => x[0] && x[0].startsWith('equity')) },
            { name: _t('Profit & Loss') },
            { name: _t('Income'), children: opts.filter(x => x[0] && x[0].startsWith('income')) },
            { name: _t('Expense'), children: opts.filter(x => x[0] && x[0].startsWith('expense')) },
            { name: _t('Other'), children: opts.filter(x => x[0] && x[0] === 'off_balance') },
            { name: _t('Net Sales (Sell-In)'), children: opts.filter(x => x[0] && x[0].startsWith('net')) },
            { name: _t('COGS'), children: opts.filter(x => x[0] && x[0].startsWith('cogs')) },
            { name: _t('Distribution Expenses'), children: opts.filter(x => x[0] && x[0].startsWith('disexp')) },
            { name: _t('Selling expenses'), children: opts.filter(x => x[0] && x[0].startsWith('sellingex')) },
            { name: _t('Marketing expenses'), children: opts.filter(x => x[0] && x[0].startsWith('marketexp')) },
            { name: _t('G&A expenses'), children: opts.filter(x => x[0] && x[0].startsWith('gaexp')) },
            
            { name: _t('Depricaition and Amortisation'), children: opts.filter(x => x[0] && x[0].startsWith('depamor')) },
        ];
        for (var i = 0; i < opts.length; i++) { console.log(opts[i][0]); }
        console.log("77777777--------777777777",opts.filter(x => x[0] && x[0] === 'depamor'))
        return data
    }
});
