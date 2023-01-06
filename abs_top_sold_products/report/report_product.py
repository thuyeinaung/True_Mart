# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class ReportProducts(models.AbstractModel):
    _name = 'report.abs_top_sold_products.report_products'
    
    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        product_records = {}
        sorted_product_records = []
        sales = self.env['sale.order'].search([('state','in',('sale','done')),('date_order','>=',docs.start_date),('date_order','<=',docs.end_date)])
        for s in sales:
            orders = self.env['sale.order.line'].search([('order_id','=',s.id)])
            for order in orders:
                if order.product_id:
                    if order.product_id not in product_records:
                        product_records.update({order.product_id:0})
                    product_records[order.product_id] += order.product_uom_qty

        for product_id, product_uom_qty in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True)[:docs.no_of_products]:
            
            sorted_product_records.append({'name':product_id.name, 'sale_price':product_id.product_tmpl_id.list_price, 'purchase_price':product_id.product_tmpl_id.standard_price, 'qty': int(product_uom_qty)})

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'products': sorted_product_records
        }

class ReportPOSProducts(models.AbstractModel):
    _name = 'report.abs_top_sold_products.report_pos_products'
    
    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        product_records = {}
        sorted_product_records = []
        pos_order = self.env['pos.order'].search([('state','in',('done','paid','invoiced')),('date_order','>=',docs.start_date),('date_order','<=',docs.end_date)])
        for pos in pos_order:
            order_lines = self.env['pos.order.line'].search([('order_id','=',pos.id)])
            for order in order_lines:
                if order.product_id:
                    if order.product_id not in product_records:
                        product_records.update({order.product_id:0})
                    product_records[order.product_id] += order.qty
        for product_id, qty in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True)[:docs.no_of_products]:
            sorted_product_records.append({'name':product_id.name, 'sale_price':product_id.product_tmpl_id.list_price, 'purchase_price':product_id.product_tmpl_id.standard_price, 'qty': int(qty)})

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'products': sorted_product_records
        }
