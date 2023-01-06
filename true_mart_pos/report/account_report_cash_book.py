# -*- coding: utf-8 -*-

from datetime import time

from odoo import models, api, _
from odoo.exceptions import UserError

class ReportCashBook(models.AbstractModel):
    _name = 'report.true_mart_pos.report_cash_book'
    _description = 'Cash Book Report'

    def _get_account_move_entry(self, accounts, init_balance, sortby,
                                display_account):

        cr = self.env.cr
        move_line = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = move_line.with_context(
                date_from=self.env.context.get('date_from'), date_to=False,
                initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id',
                                           'm').replace('account_move_line',
                                                        'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, 0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                    '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                    NULL AS currency_id,\
                    '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                    '' AS partner_name\
                    FROM account_move_line l\
                    LEFT JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)
        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = move_line._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace(
            'account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
                FROM account_move_line l\
                JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                JOIN account_account acc ON (l.account_id = acc.id) \
                WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_res.append(res)

        return account_res

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = 'movement'
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        account_ids = data['form']['account_ids']
        accounts = self.env['account.account'].search(
            [('id', 'in', account_ids)])
        accounts_res = self.with_context(
            data['form'].get('used_context', {}))._get_account_move_entry(
            accounts,
            init_balance,
            sortby,
            display_account)
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
        }
        
        
class ReportCashBookExcel(models.Model):
    _name = "report.true_mart_pos.report_cash_book_excel"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.true_mart_pos.report_cash_book']
        results = report_obj.get_report_values(obj, data)
        sheet = workbook.add_worksheet()

#         format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True,
#                                        'align': 'center', 'bold': True, 'bg_color': '#bfbfbf', 'valign': 'vcenter'})
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True,
                                       'align': 'center', 'bold': True, 'bg_color': '#16365c', 'valign': 'vcenter', 'color': '#ffffff'})
#         format2 = workbook.add_format({'font_size': 12, 'align': 'left', 'right': True, 'left': True,
#                                        'bottom': True, 'top': True, 'bold': True, 'bg_color': '#bfbfbf'})
        format2 = workbook.add_format({'font_size': 12, 'align': 'left', 'right': True, 'left': True,
                                       'bottom': True, 'top': True, 'bold': True, 'bg_color': '#16365c', 'color': '#ffffff'})
#         format3 = workbook.add_format({'font_size': 12, 'align': 'right', 'right': True, 'left': True,
#                                        'bottom': True, 'top': True, 'bold': True, 'bg_color': '#bfbfbf'})
        format3 = workbook.add_format({'font_size': 12, 'align': 'right', 'right': True, 'left': True,
                                       'bottom': True, 'top': True, 'bold': True, 'bg_color': '#16365c', 'color': '#ffffff'})
        format4 = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': True, 'right': True, 'left': True,
                                       'bottom': True, 'top': True})
        format5 = workbook.add_format({'font_size': 10, 'align': 'right', 'bold': True, 'right': True, 'left': True,
                                       'bottom': True, 'top': True})
        format6 = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': False, 'right': True, 'left': True,
                                       'bottom': True, 'top': True, 'text_wrap':'true'})
        format7 = workbook.add_format({'font_size': 10, 'align': 'right', 'bold': False, 'right': True, 'left': True,
                                       'bottom': True, 'top': True})
        format8 = workbook.add_format({'font_size': 10, 'align': 'left', 'bold': False, 'right': True, 'left': True,
                                       'bottom': True, 'top': True, 'num_format': 'yyyy-mm-dd'})

        sheet.set_row(0, 40)
        sheet.set_row(2, 40)
        sheet.set_column(0, 1, 13)
        sheet.set_column(2, 5, 25)
        sheet.set_column(6, 8, 15)

        sheet.merge_range('A1:J1', "Cash Book Report", format1)

        sheet.merge_range('A3:B3', "Journals", format4)
        sheet.write('C3', ', '.join([lt or '' for lt in results['print_journal']]), format6)
        sheet.write('G3', 'Target Moves', format4)
        if data['form']['target_move'] == 'posted':
            sheet.merge_range('H3:I3', 'All Posted Entries', format6)
        else:
            sheet.write('H3:I3', 'All Entries', format6)

        sheet.merge_range('A4:B4', "Display Account", format4)
        if data['form']['display_account'] == 'all':
            sheet.write('C4', 'All', format6)
        elif data['form']['display_account'] == 'movement':
            sheet.write('C4', 'With Movements', format6)
        else:
            sheet.write('C4', 'With balance is not equal to 0', format6)
        sheet.write('G4', 'Sorted By', format4)
        if data['form']['sortby'] == 'sort_date':
            sheet.merge_range('H4:I4', 'Date', format6)
        else:
            sheet.write('H4:I4', 'Journal & Partner', format6)

        if data['form']['date_from']:
            sheet.merge_range('A5:B5', "Date From", format4)
            sheet.write('C5', data['form']['date_from'], format6)
        if data['form']['date_to']:
            sheet.write('G5', "Date To", format4)
            sheet.merge_range('H5:I5', data['form']['date_to'], format6)
        
        sheet.write('A7', "Date ", format2)
        sheet.write('B7', "JRNL", format2)
        sheet.write('C7', "Partner", format2)
        sheet.write('D7', "Ref", format2)
        sheet.write('E7', "JRNL Code", format2)
        sheet.write('F7', "Entry Label", format2)
        sheet.write('G7', "Debit", format3)
        sheet.write('H7', "Credit", format3)
        sheet.write('I7', "Balance", format3)
        row = 7
        col = 0
        for account in results['Accounts']:            
            for line in account['move_lines']:
                col = 0             
                sheet.write(row, col, line['ldate'], format8)
                sheet.write(row, col + 1, line['lcode'], format6)
                sheet.write(row, col + 2, line['partner_name'], format6)
                sheet.write(row, col + 3, line['lref'] or '', format6)
                sheet.write(row, col + 4, line['move_name'], format6)
                sheet.write(row, col + 5, line['lname'], format6)
                sheet.write(row, col + 6, line['debit'], format7)
                sheet.write(row, col + 7, line['credit'], format7)
                sheet.write(row, col + 8, line['balance'], format7)
                row += 1
            col = 0
            sheet.merge_range(row, col, row, col + 5, account['code'] + account['name'], format4)
            sheet.write(row, col + 6, account['debit'], format5)
            sheet.write(row, col + 7, account['credit'], format5)
            sheet.write(row, col + 8, account['balance'], format5)
            row += 1