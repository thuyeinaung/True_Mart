# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountingReportExcel(models.TransientModel):
    _inherit = "accounting.report"
    
    def _print_report(self, data):
        if self._context.get('excel_report'):
            data['form'].update(self.read(
                ['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter',
                 'label_filter', 'target_move'])[0])
            return self.env.ref('true_mart_pos.action_report_financial_excel').report_action(
                self, data=data, config=False)
        else:
            return super(AccountingReportExcel, self)._print_report(data)