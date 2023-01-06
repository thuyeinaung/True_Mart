# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools
from openerp.exceptions import Warning
# from odoo.exceptions import RedirectWarning, UserError, ValidationError
import random
from datetime import date, datetime

class ReportPaperFormateInherit(models.Model):

    _inherit = "report.paperformat"

    page_height = fields.Float('Page height (mm)', default=False)
    page_width = fields.Float('Page width (mm)', default=False)

class pos_membership_setting(models.Model):
    _name = 'pos.membership.setting'

    name  = fields.Char('Name', default='Configuration for POS Membership Cards')
    issue_date  =  fields.Datetime('Issue Date', default = datetime.now(), )
    default_name  = fields.Char('Name')
    #discount_amount  =  fields.Float('Discount (%)')
    pricelist_id  =  fields.Many2one('product.pricelist', string='Pricelist')
    
    allow_one_customer = fields.Boolean('Allow One Membership Card per Customer')
    apply_membershipcards = fields.Boolean(' Ignore Membership Discount If Discount Already Exists')
    apply_membership_discount = fields.Selection([('ignore_all_orderlines', 'Ignore membership discounts for all orderlines'), ('ignore_specific_orderlines', 'Ignore membership discounts for only those orderlines where discount exists.') ])

class pos_membership(models.Model):
    _name = 'pos.membership'


    
    def print_membership_card_report(self):

        paper_formate = self.env['ir.model.data'].xmlid_to_object('pos_membership_odoo.paper_format')
        paper_formate.page_height = self.membership_template.label_hight or 150
        paper_formate.page_width = self.membership_template.label_width  or 100

        qty = self.membership_template.print_qty

        if qty is 0:
            qty = 1
        else:
            qty = self.membership_template.print_qty


        #return self.env['report'].get_action(self, 'pos_membership_odoo.report_pos_membership_cards')
        return self.env.ref('pos_membership_odoo.action_membership_cards').report_action(self)
        
    @api.one
    def apply_membership_cards(self, code):
    	membership_code_record =self.search([('membership_code', '=',code)])
    	if len(membership_code_record) == 1:
    		membership_record = membership_code_record[0]
    		return True
    	else:
    		return False

    @api.multi
    def search_membership_cards(self, code):
        membership_code_record = self.search([('membership_code', '=', code)])
        if membership_code_record:
            #return [ membership_code_record.membership_code, membership_code_record.membership_id.discount_amount, membership_code_record.expiry_date, membership_code_record.partner_id.id ]
            return [ membership_code_record.membership_code, membership_code_record.membership_id.pricelist_id.id, membership_code_record.expiry_date, membership_code_record.partner_id.id ]
            

    @api.one
    def apply_pricelist(self, pricelist_id):
        main_dict = {}
        product_obj = self.env['product.product']
        product_ids = product_obj.search([])
        
        product_pricelist = self.env['product.pricelist']
        product_pricelist.browse(pricelist_id)
        for product_id in product_ids:
            
            price = product_pricelist.price_get(product_id.id, qty=1, partner=None)
            price.update({'product_id':product_id.id })
            main_dict.update({product_id.id : price})
    	
        return main_dict
    	                		
    @api.model
    def create(self, vals):
        pos_config_obj = self.env['pos.membership.setting']
        code =(random.randrange(1111111111111,9999999999999))
        membership = self.env['pos.membership'].search_count([('partner_id','=', vals['partner_id'])])
        membership_conf = pos_config_obj.search([])[0]

        if membership > 1 and membership_conf.allow_one_customer == True:
            raise Warning(_('Please configure membership'))
        else:
            hide_barcode = str(code)
            #hide_barcode = hide_barcode[:8].ljust(len(hide_barcode), "*")
            hide_barcode = hide_barcode[:13].ljust(len(hide_barcode), "*")
            vals.update({'membership_code': str(code),'hide_barcode': hide_barcode})
            return super(pos_membership, self).create(vals)
        
    def _set_default_template(self):

        return self.env['pos.membership.template.settings'].search([('if_default_template','=',True)]).id




    membership_id  =  fields.Many2one('pos.membership.setting', string='Membership')
    name  = fields.Char('Name')
    membership_code = fields.Char('Membership Code')
    hide_barcode = fields.Char('Hidden Barcode')
    issue_date  =  fields.Date(default = datetime.now(), )
    expiry_date  = fields.Date('Expiry Date')
    partner_id  =  fields.Many2one('res.partner', string='Customer')
    membership_template  =  fields.Many2one('pos.membership.template.settings', string='Template',default=_set_default_template)
    # print_front_report = fields.Many2one('pos.membership.front.image')
    # print_back_report = fields.Many2one('pos.membership.back.image')
    
class PosMembershipFrontImage(models.Model):

    _name = 'pos.membership.front.image'

    partner_id  =  fields.Many2one('res.partner')
    membership_template = fields.Many2one('pos.membership.template.settings')
    
    def print_membership_card_front_img(self):
        curr_card = self.env['pos.membership'].search([('id','=',self._context.get('active_id'))])
        
        if curr_card.membership_template:
            self.membership_template = curr_card.membership_template.id
        else:
            self.membership_template = False

        if curr_card.partner_id:
            self.partner_id = curr_card.partner_id.id
        else:
            self.partner_id = False
        
        #return self.env['report'].get_action(self,'pos_membership_odoo.report_pos_membership_card_front_image')
        return self.env.ref('pos_membership_odoo.action_membership_card_front_img').report_action(self)

class PosMembershipBackImage(models.Model):

    _name = 'pos.membership.back.image'

    partner_id  =  fields.Many2one('res.partner')
    membership_template = fields.Many2one('pos.membership.template.settings')
    membership_code = fields.Char('Membership Code')
    hide_barcode = fields.Char('Hidden Barcode')
    
    def print_membership_card_back_img(self):
        curr_card = self.env['pos.membership'].search([('id','=',self._context.get('active_id'))])
        
        if curr_card.membership_template:
            self.membership_template = curr_card.membership_template.id
        else:
            self.membership_template = False

        if curr_card.membership_code:
            self.membership_code = curr_card.membership_code
        else:
            self.membership_code = False

        if curr_card.hide_barcode:
            self.hide_barcode = curr_card.hide_barcode
        else:
            self.hide_barcode = False

        if curr_card.partner_id:
            self.partner_id = curr_card.partner_id.id
        else:
            self.partner_id = False
        
        #return self.env['report'].get_action(self,'pos_membership_odoo.report_pos_membership_card_back_image')
        return self.env.ref('pos_membership_odoo.action_membership_card_back_img').report_action(self)

class PosMembershipFullFrontImage(models.Model):

    _name = 'pos.membership.full.front.image'

    partner_id  =  fields.Many2one('res.partner')
    membership_template = fields.Many2one('pos.membership.template.settings')
    
    def print_membership_card_full_front_img(self):
        curr_card = self.env['pos.membership'].search([('id','=',self._context.get('active_id'))])
        
        if curr_card.membership_template:
            self.membership_template = curr_card.membership_template.id
        else:
            self.membership_template = False

        if curr_card.partner_id:
            self.partner_id = curr_card.partner_id.id
        else:
            self.partner_id = False
        
        #return self.env['report'].get_action(self,'pos_membership_odoo.report_pos_membership_card_full_front_image')
        return self.env.ref('pos_membership_odoo.action_membership_card_full_front_img').report_action(self)

class PosMembershipFullBackImage(models.Model):

    _name = 'pos.membership.full.back.image'

    partner_id  =  fields.Many2one('res.partner')
    membership_template = fields.Many2one('pos.membership.template.settings')
    membership_code = fields.Char('Membership Code')
    hide_barcode = fields.Char('Hidden Barcode')
    
    def print_membership_card_full_back_img(self):
        curr_card = self.env['pos.membership'].search([('id','=',self._context.get('active_id'))])
        
        if curr_card.membership_template:
            self.membership_template = curr_card.membership_template.id
        else:
            self.membership_template = False

        if curr_card.membership_code:
            self.membership_code = curr_card.membership_code
        else:
            self.membership_code = False

        if curr_card.hide_barcode:
            self.hide_barcode = curr_card.hide_barcode
        else:
            self.hide_barcode = False

        if curr_card.partner_id:
            self.partner_id = curr_card.partner_id.id
        else:
            self.partner_id = False
        
        #return self.env['report'].get_action(self,'pos_membership_odoo.report_pos_membership_card_full_back_image')
        return self.env.ref('pos_membership_odoo.action_membership_card_full_back_img').report_action(self)


class pos_membership_template_setting(models.Model):

    _name='pos.membership.template.settings'
    _rec_name = 'card_name'

    card_name = fields.Char("Name")
    if_default_template = fields.Boolean("Default Template")

    card_front_image = fields.Binary("Front Image")
    card_back_image = fields.Binary("Back Image")

    print_qty = fields.Integer("Quantity", default = 1)

    label_hight =  fields.Float("Label Height (px)")
    label_width =  fields.Float("Label Width (%)")
    
    barcode_hight =  fields.Float("Barcode Height (px)")
    barcode_width =  fields.Float("Barcode Width (px)")
    
    @api.model  
    def create(self, vals):
        res = super(pos_membership_template_setting, self).create(vals)
        rec = self.search([('if_default_template','=',True)])

        if len(rec) > 1:
            raise Warning(_('Another template is allready selected as default template.'))
        return res

    @api.multi
    def write(self, vals):
        res = super(pos_membership_template_setting, self).write(vals)
        rec = self.search([('if_default_template','=',True)])
        
        if len(rec) > 1:
            raise Warning(_('Another template is allready selected as default template.'))
        return res
    
class PosOrderMembershipCode(models.Model):
    _inherit = "pos.order"

    pos_order_membership_code  =  fields.Many2one('pos.membership', string='Membership Code')

    # @api.model
    # def _process_order(self, pos_order):

    #     res = super(PosOrderMembershipCode,self)._process_order(pos_order)

    #     pos_membership = self.env['pos.membership'].search([])
    #     print "********************************************************************* Validate call",pos_membership

    #     return res

class PosGroupBy(models.Model):
    _inherit = "report.pos.order"

    pos_order_membership_code  =  fields.Many2one('pos.membership', string='Membership Code')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_pos_order')
        self._cr.execute("""
            CREATE OR REPLACE VIEW report_pos_order AS (
                SELECT
                    MIN(l.id) AS id,
                    COUNT(*) AS nbr_lines,
                    s.date_order AS date,
                    SUM(l.qty) AS product_qty,
                    SUM(l.qty * l.price_unit) AS price_sub_total,
                    SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
                    SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
                    (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS average_price,
                    SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                    s.id as order_id,
                    s.partner_id AS partner_id,
                    s.state AS state,
                    s.user_id AS user_id,
                    s.location_id AS location_id,
                    s.company_id AS company_id,
                    s.sale_journal AS journal_id,
                    s.pos_order_membership_code AS pos_order_membership_code,
                    l.product_id AS product_id,
                    pt.categ_id AS product_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pt.pos_categ_id,
                    pc.stock_location_id,
                    s.pricelist_id,
                    s.session_id,
                    s.invoice_id IS NOT NULL AS invoiced
                FROM pos_order_line AS l
                    LEFT JOIN pos_order s ON (s.id=l.order_id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                    LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                    LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                GROUP BY
                    s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id, s.location_id, s.company_id, s.sale_journal,
                    s.pricelist_id, s.invoice_id, s.create_date, s.session_id,s.pos_order_membership_code,
                    l.product_id,
                    pt.categ_id, pt.pos_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pc.stock_location_id
                HAVING
                    SUM(l.qty * u.factor) != 0
            )
        """)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
