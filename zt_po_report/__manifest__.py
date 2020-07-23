# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2020-TODAY ZT Technologies
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

    "name": "PO xlsx Report",
    "summary": "Module For PO Summary Report",
    "version": '13.0.0.0.0',
    "sequence": 10,
    "author": "ZT-DEV",
    "license": "AGPL-3",
    "depends":
        ['purchase','report_xlsx'],
    "data":
        [
            'views/purchase_order_wizard_view.xml',
            'report/report_xls.xml'],
    "installable": True,
    "application": True,

}
