# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class top_client_wizard_report(models.AbstractModel):

    _name='report.pos_membership_odoo.top_client_wizard_report'
    
    
    @api.model
    def get_report_values(self, docids, data):
        
        self.model = self.env.context.get('active_model')
        top_client_card = self.env['pos.membership.top.clients.cards'].browse(docids)
        
        pos_membership = self.env['pos.membership'].search([
            ('issue_date','>=',top_client_card.start_dt),
            ('expiry_date','<=',top_client_card.end_dt),
            ], limit=top_client_card.no_of_top_clients)

        if not pos_membership:
            raise UserError(_("Please enter a valid date and try again."))
            return
        
        
        #docs = self.env[self.model].browse(self.env.context.get('active_id'))
        #report_lines = self.button_calculate_rep(data.get('form'))
        return {
            
            'doc_ids': docids,

            'doc_model': 'pos.membership.top.clients.cards',

            'docs': top_client_card,

            'member_list' : pos_membership,
            
            #'doc_ids': self.ids,
            #'doc_model': self.model,
            #'data': data['form'],
            #'docs': docs,
            #'time': time,
            #'button_calculate_rep': report_lines,
        }
        
        

    
    
    '''@api.model
    def render_html(self, docids, data=None):

        Report = self.env['report']
        payment_report = Report._get_report_from_name('pos_membership_odoo.top_client_wizard_report')
        
        top_client_card = self.env['pos.membership.top.clients.cards'].browse(docids)
        
        pos_membership = self.env['pos.membership'].search([
            ('issue_date','>=',top_client_card.start_dt),
            ('expiry_date','<=',top_client_card.end_dt),
            ], limit=top_client_card.no_of_top_clients)

        if not pos_membership:
            raise UserError(_("Please enter a valid date and try again."))
            return
        
        docargs = {
            
            'doc_ids': docids,

            'doc_model': 'pos.membership.top.clients.cards',

            'docs': top_client_card,

            'member_list' : pos_membership,
        }

        return Report.render('pos_membership_odoo.top_client_wizard_report', docargs)'''
    
    
       

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
