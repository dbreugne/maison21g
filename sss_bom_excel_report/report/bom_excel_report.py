# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class BOMExcelReport(models.AbstractModel):
    _name = "report.sss_bom_excel_report.bom_report_xlsx"
    _description = "BOM All Qty And UOM report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('mrp.bom')
        bold = workbook.add_format({'font_color':'white','bg_color':'#380036','align':'center','valign':'center','font_size':12})
        size = workbook.add_format({'bold':True,'align':'left'})
        size1 = workbook.add_format({'bold':True,'align':'left', 'bg_color': '#E9ECEF'})
        size2 = workbook.add_format({'bold':False,'align':'left'})
        font_size = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': False, 'right': True, 'left': True,
                                    'bottom': True, 'top': True})

        sheet.set_column(0,7,25)
        sheet.write(0,0,'Product',size)
        sheet.write(0,1,'Last Updated on',size)
        sheet.write(0,2,'Reference',size)
        sheet.write(0,3,'BoM Lines',size)
        sheet.write(0,4,'BoM Type',size)
        sheet.write(0,5,'Company',size)
        sheet.write(0,6,'Quantity',size)
        sheet.write(0,7,'Unit of Measure',size)

        col = 0
        row = 1
        bom_ids = self.env['mrp.bom'].search([('id', 'in', objs.ids)])
        bom_type_lst = []
        count = []
        for rec in objs:
            if rec.type not in bom_type_lst:
                bank_data = self.env['mrp.bom'].read_group([('id', 'in', objs.ids)], ['id'], ['type'])
                bom_type_lst.append(rec.type)
                # bom_type_lst.append(count(rec.id))
        for bom_type_count in bank_data:
            count.append(bom_type_count.get('type_count'))

        # for bom_type in bom_type_lst:
        for bom_type,count in zip(bom_type_lst,count):
            sheet.write(row,col,bom_type + ' ' + '('+ str(count) + ')',size1)
            sheet.write(row,col+1,' ',size1)
            sheet.write(row,col+2,' ',size1)
            sheet.write(row,col+3,' ',size1)
            sheet.write(row,col+4,' ',size1)
            sheet.write(row,col+5,' ',size1)
            sheet.write(row,col+6,' ',size1)
            sheet.write(row,col+7,' ',size1)
            for rec in objs:
                if rec.type == bom_type:
                    # product_id_count = self.env['mrp.bom'].read_group([('id', 'in', objs.ids)], ['product_tmpl_id'], ['product_tmpl_id'])
                    row += 1
                    sheet.write(row,col,'['+ rec.product_tmpl_id.default_code + ']' + ' ' + rec.product_tmpl_id.name + ' ' + '(' + str(len(rec.product_tmpl_id)) + ')',size1)
                    sheet.write(row,col+1,' ',size1)
                    sheet.write(row,col+2,' ',size1)
                    sheet.write(row,col+3,' ',size1)
                    sheet.write(row,col+4,' ',size1)
                    sheet.write(row,col+5,' ',size1)
                    sheet.write(row,col+6,rec.product_qty,size1)
                    sheet.write(row,col+7,' ',size1)
                    row += 1
                    if rec.product_tmpl_id.id == rec.product_tmpl_id.id:
                        sheet.write(row,col,'['+ rec.product_tmpl_id.default_code + ']' + ' ' + rec.product_tmpl_id.name,size2)
                        # sheet.write(row,col+1,str(rec.write_date),size2)
                        sheet.write(row,col+1,rec.write_date.strftime("%m/%d/%Y, %H:%M:%S"),size2)
                        sheet.write(row,col+2,rec.code,size2)
                        sheet.write(row,col+4,rec.type,size2)
                        sheet.write(row,col+5,rec.company_id.name,size2)
                        for line in rec.bom_line_ids:
                            sheet.write(row,col+3,'['+ line.product_id.default_code + ']' + ' ' +line.product_id.name,size2)
                            sheet.write(row,col+6,(rec.product_qty * line.product_qty),size2)
                            sheet.write(row,col+7,line.product_uom_id.name,size2)
                            row += 1
            row += 1
