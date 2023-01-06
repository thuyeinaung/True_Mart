# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountPrintJournalExcel(models.TransientModel):
    _inherit = "account.print.journal"
    
    def _print_report(self, data):
        if self._context.get('excel_report'):
            data = self.pre_print_report(data)
            data['form'].update({'sort_selection': self.sort_selection})
            return self.env.ref('true_mart_pos.action_report_journal_excel').report_action(
                self, data=data)
        else:
            return super(AccountPrintJournalExcel, self)._print_report(data)