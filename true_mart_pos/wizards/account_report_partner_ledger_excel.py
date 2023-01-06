# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountPartnerLedgerExcel(models.TransientModel):
    _inherit = "account.report.partner.ledger"
    
    def _print_report(self, data):
        if self._context.get('excel_report'):
            data = self.pre_print_report(data)
            data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
            return self.env.ref('true_mart_pos.action_report_partnerledger_excel').report_action(
                self, data=data)
        else:
            return super(AccountPartnerLedgerExcel, self)._print_report(data)