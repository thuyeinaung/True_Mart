# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    audio_url = fields.Char('Audio', readonly=True, help='Link to saved audio record of call on servers your telephony provider.')