# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class CashBookWizard(models.TransientModel):
    _name = 'account.cash.book.report'
    _description = 'Account Cash Book Report'
    
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True, default=lambda self: self.env['account.journal'].search([]))
    account_ids = fields.Many2many('account.account', 'account_report_cashbook_account_rel',
                                   'report_id', 'account_id', string='Accounts')
    company_id = fields.Many2one('res.company', string='Company',
                                readonly=True,
                                default=lambda self: self.env.user.company_id)
                                   
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    display_account = fields.Selection([('all','All'), ('movement','With movements'), 
                                        ('not_zero','With balance is not equal to 0'),], 
                                        string='Display Accounts', required=True, default='movement')
    initial_balance = fields.Boolean(string='Include Initial Balances',
                                    help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')
    
    @api.onchange('company_id')
    def onchange_company_ids(self):      
        if self.company_id:
            journals = self.env['account.journal'].search([('type', '=', 'cash'),('company_id','=',self.company_id.id)])  
            accounts = []
            for journal in journals:
                accounts.append(journal.default_credit_account_id.id)
            values = {'account_ids':accounts or False}
            return self.update(values)
    
    @api.onchange('account_ids')
    def onchange_account_ids(self):
        if self.account_ids:            
            company_id = []
            for account in self.account_ids:
                company_id.append(account.company_id.id)
                
            journals = self.env['account.journal'].search( [('type', '=', 'cash'),('company_id','in',company_id)])  
            
            self.journal_ids = journals if journals else []    
                    
            accounts = []
            for journal in journals:
                accounts.append(journal.default_credit_account_id.id)
            domain = {'account_ids': [('id', 'in', accounts)]}
            return {'domain': domain}
        
    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result
        
    #@api.multi
    def check_report(self):
        self.ensure_one()
        if self.initial_balance and not self.date_from:
            raise UserError(_("You must choose a Start Date"))
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 
                                  'target_move','display_account','account_ids', 'sortby', 'initial_balance'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self.env.ref(
            'true_mart_pos.action_report_cash_book').report_action(self,
                                                                         data=data)
            
class AccountReportCashBookExcel(models.TransientModel):
    _inherit = "account.cash.book.report"

    def check_report(self):
        if self._context.get('excel_report'):
            self.ensure_one()
            if self.initial_balance and not self.date_from:
                raise UserError(_("You must choose a Start Date"))
            data = {}
            data['ids'] = self.env.context.get('active_ids', [])
            data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
            data['form'] = self.read(
                                     ['date_from', 'date_to', 'journal_ids', 'target_move',
                                      'display_account',
                                      'account_ids', 'sortby', 'initial_balance'])[0]
            used_context = self._build_contexts(data)
            data['form']['used_context'] = dict(used_context,
                                            lang=self.env.context.get(
                                                'lang') or 'en_US')
            return self.env.ref(
                                'true_mart_pos.action_report_cash_book_excel').report_action(self,
                                                                         data=data)
        else:
            return super(AccountReportCashBookExcel, self).check_report()
    
    