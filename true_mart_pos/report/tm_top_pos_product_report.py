# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class TMPOSTopProductReport(models.Model):
    _name = 'tm.pos.top.product.report'
    _description = "True Mart POS Top Product Report"
    _auto = False
    _order = "total_pos_quantity desc"
    
    company_id = fields.Many2one('res.company',string='Company',readonly=True)
    product_id = fields.Many2one('product.product',string='Product',readonly=True)
    product_name = fields.Char(string='Product Name',readonly=True)
    pro_sale_price = fields.Float('Sale Price', digits=dp.get_precision('Product Sale Price'), readonly=True)
    pro_purchase_price = fields.Float('Purchase Price', digits=dp.get_precision('Product Purchase Price'), readonly=True)
    total_pos_quantity = fields.Float(string='Total POS Qty', default=0.0,readonly=True)
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute("""CREATE OR REPLACE VIEW %s AS (
            SELECT 
                max(pol.id) AS id,
                po.company_id as company_id,
                pol.product_id as product_id,
                pt.name as product_name,
                pt.list_price as pro_sale_price,
                prop.value_float as pro_purchase_price,
                sum(qty) as total_pos_quantity 
            FROM pos_order_line pol 
                JOIN pos_order po ON pol.order_id = po.id 
                JOIN product_product pp on pol.product_id = pp.id                   
                JOIN product_template pt on pp.product_tmpl_id=pt.id
                JOIN ir_property prop on prop.res_id = 'product.product,' || pp.id
            WHERE po.state in ('done','paid','invoiced')  
            GROUP BY pt.name,pt.list_price,pol.product_id,po.company_id,prop.value_float
            ORDER BY total_pos_quantity DESC
        )
        """ % self._table)