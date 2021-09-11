from odoo import api, fields, models

from lxml import etree

class ManageIframe(models.Model):
    _name = 'bcc.iframe'
    _rec_name = 'name'

    name= fields.Char('Name',default="Analysis")

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(ManageIframe,self).fields_view_get(view_id=view_id, view_type=view_type,
                                           toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for sheet in doc.xpath("//sheet"):
                parent = sheet.getparent()
                index = parent.index(sheet)
                for child in sheet:
                    parent.insert(index, child)
                    index += 1
                parent.remove(sheet)
            res['arch'] = etree.tostring(doc)
        return res
