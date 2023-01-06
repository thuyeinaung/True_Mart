# -*- coding: utf-8 -*-

from odoo import models

class AccountTaxReportExcel(models.TransientModel):
    _inherit = 'account.tax.report'

    def _print_report(self, data):
        if self._context.get('excel_report'):
            return self.env.ref('true_mart_pos.action_report_account_tax_excel').report_action(
                self, data=data)
        else:
            return super(AccountTaxReportExcel, self)._print_report(data)