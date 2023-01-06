# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountBalanceReportExcel(models.TransientModel):
    _inherit = "account.balance.report"
    
    def _print_report(self, data):
        if self._context.get('excel_report'):
            data = self.pre_print_report(data)
            records = self.env[data['model']].browse(data.get('ids', []))
            return self.env.ref('true_mart_pos.action_report_trial_balance_excel').report_action(
                records, data=data)
        else:
            return super(AccountBalanceReportExcel, self)._print_report(data)
