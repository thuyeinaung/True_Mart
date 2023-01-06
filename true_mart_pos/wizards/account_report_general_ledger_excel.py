# -*- coding: utf-8 -*-

from odoo import fields, models, _

class AccountReportGeneralLedgerExcel(models.TransientModel):
    _inherit = "account.report.general.ledger"
    
    def _print_report(self, data):
        if self._context.get('excel_report'):
            data = self.pre_print_report(data)
            data['form'].update(self.read(['initial_balance', 'sortby'])[0])
            if data['form'].get('initial_balance') and not data['form'].get('date_from'):
                raise UserError(_("You must define a Start Date"))
            records = self.env[data['model']].browse(data.get('ids', []))
            return self.env.ref('true_mart_pos.action_report_general_ledger_excel').report_action(
                records, data=data, config=False)
        else:
            return super(AccountReportGeneralLedgerExcel, self)._print_report(data)