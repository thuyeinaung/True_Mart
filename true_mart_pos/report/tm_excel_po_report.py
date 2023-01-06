# -*- coding: utf-8 -*-
import datetime
from datetime import datetime
import pytz
from odoo import models, fields


class DmsStockReportXls(models.AbstractModel):
    _name = 'report.true_mart_pos.tm_po_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_po_data(self, data):

        lines = []
        open_qty = []
        from_date = data.from_date        
        to_date = data.to_date         
        
        # self._cr.execute(
                         # '''select am.date Date,sol.name Product_Name, rp.name Customer_Name,ai.number Invoice_Number,so.name SO_Number,  qty_invoiced Qty,price_unit Sale_Price, price_total Sale_Amount
                             # ,aj.name Type_of_Payment
                            # from sale_order_line sol
                            # inner join sale_order so on sol.order_id = so.id
                            # inner join res_partner rp on rp.id = so.partner_id
                            # inner join account_invoice ai on so.name = ai.origin
                            # inner join account_move am on am.name = ai.number
                            # -- inner join account_journal aj
                            # -- on aj.id = am.journal_id
                            # left join account_invoice_payment_rel apr on ai.id = apr.invoice_id
                            # left join account_payment ap on ap.id = apr.payment_id
                            # left join account_journal aj on aj.id = ap.journal_id
                            # where am.date between %s and %s
                            # order by am.date , so.name''',(from_date,to_date)
                         # )
        # so_query_obj = self._cr.dictfetchall()
        
        self._cr.execute(
                         '''Select am.date Date,rp.name Vendor_Name,ai.number Bill_Number,po.name PO_Number,ap.amount Amount, aj.name Type_of_Payment from purchase_order po
                            inner join res_partner rp
                            on rp.id = po.partner_id
                            inner join account_invoice ai
                            on po.name = ai.origin
                            inner join account_move am
                            on am.name = ai.number
                            -- inner join account_journal aj
                            -- on aj.id = am.journal_id
                            left join account_invoice_payment_rel apr
                            on ai.id = apr.invoice_id
                            left join account_payment ap
                            on ap.id = apr.payment_id
                            left join account_journal aj
                            on aj.id = ap.journal_id
                            where am.date between %s and %s
                            order by am.date ''',(from_date,to_date)
                         )
        po_query_obj = self._cr.dictfetchall()
        

        return po_query_obj
            
    def generate_xlsx_report(self, workbook, data, obj):
        
        colors = {
            'Lavender': '#E6E6FA',
        }
       
        po_query_obj = self.get_po_data(obj)     
        

        sheet = workbook.add_worksheet('PO Report')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 11, 'align': 'center', 'bold': True, 'bg_color':colors['Lavender']})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 9, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 9, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 9, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        #date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','bold': True,'font_size':9,'align':'left'})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        sheet.merge_range('A1:I2', 'Purchases Order Report', format0)
      

        sheet.write(4, 0, 'No.', format21)
        sheet.write(4, 1, 'Date', format21)
        sheet.write(4, 2, 'Vendor Name', format21)
        sheet.write(4, 3, 'Bill Number', format21)
        sheet.write(4, 4, 'PO Number', format21)
        sheet.write(4, 5, 'Amount', format21)
        sheet.write(4, 6, 'Type of Payment', format21)  
        
        prod_row = 5
        prod_col = 0
        prod_no = 1

        for each in po_query_obj:   
            
            # sheet.write(prod_row, prod_col, each['date'], date_format)date_style
            sheet.write(prod_row, prod_col, prod_no , font_size_8_r)
            sheet.write(prod_row, prod_col + 1, each['date'], date_format)
            sheet.write(prod_row, prod_col + 2, each['vendor_name'], font_size_8)
            sheet.write(prod_row, prod_col + 3, each['bill_number'], font_size_8)
            sheet.write(prod_row, prod_col + 4, each['po_number'], font_size_8_l) 
            sheet.write(prod_row, prod_col + 5, each['amount'], font_size_8_r)
            sheet.write(prod_row, prod_col + 6, each['type_of_payment'], font_size_8_r)
            # sheet.write(prod_row, prod_col + 6, each['sale_price'], font_size_8_r)
            # sheet.write(prod_row, prod_col + 7, each['sale_amount'], font_size_8_r)
            # sheet.write(prod_row, prod_col + 8, each['type_of_payment'], font_size_8_r)    
            prod_row = prod_row + 1
            prod_no = prod_no + 1