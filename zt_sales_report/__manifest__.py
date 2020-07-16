# -*- coding: utf-8 -*-
##############################################################################
#
#    ZT Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY ZT Technologies
#    Author: Libu S
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{

    "name": "Sale And CRM Based xlsx Report",
    "summary": "Base module to create xlsx report",
    "version": '13.0.0.0.0',
    "sequence": 10,
    "author": "ZT-DEV",
    'summary': 'Analyse Your Sales And CRM Performance',
    "license": "AGPL-3",
    "depends":
        ['sale','base','crm','report_xlsx'],
    "data":
        ['views/sale_order_wizard_view.xml',
         'views/crm_view.xml',
         'report/report_xls.xml'],
    "installable": True,
    "application": True,

}
