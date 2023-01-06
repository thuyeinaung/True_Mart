# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, datetime

class pos_membership_top_clients_cards(models.TransientModel):

    _name='pos.membership.top.clients.cards'

    start_dt = fields.Date('Start Date', required = True)
    end_dt = fields.Date('End Date', required = True)
    no_of_top_clients = fields.Integer("Number of clients membership(Top)")

    @api.multi
    def membership_generate_report(self):
        
        #return self.env['report'].get_action(self, 'pos_membership_odoo.top_client_wizard_report')
        return self.env.ref('pos_membership_odoo.action_top_clients_membership_cards').report_action(self)
