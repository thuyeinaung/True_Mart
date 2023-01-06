from odoo import models, api, fields, osv, _
import xlwt
import base64
from odoo.exceptions import UserError, ValidationError

class DmsStockHistoryXlsWizard(models.TransientModel):
    _name = 'tm.so.report.xls.wizard'
    
    from_date = fields.Date('From Date')
    to_date  = fields.Date('To Date')    
    
    @api.multi
    def export_so_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tm.so.report.xls.wizard'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('true_mart_pos.tm_so_report_xlsx').report_action(self, data=datas)       