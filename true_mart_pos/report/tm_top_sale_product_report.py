# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class TMTopSaleProductReport(models.Model):
    _name = 'tm.top.sale.product.report'
    _description = "True Mart Top Sale Report"
    _auto = False
    _order = "total_sale_quantity desc"
    
    company_id = fields.Many2one('res.company',string='Company',readonly=True)
    product_id = fields.Many2one('product.product',string='Product',readonly=True)
    product_name = fields.Char(string='Product Name',readonly=True)
    pro_sale_price = fields.Float('Sale Price', digits=dp.get_precision('Product Sale Price'), readonly=True)
    pro_purchase_price = fields.Float('Purchase Price', digits=dp.get_precision('Product Purchase Price'), readonly=True)
    total_sale_quantity = fields.Float(string='Total Sale Qty', default=0.0,readonly=True)
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute("""CREATE OR REPLACE VIEW %s AS (
            SELECT 
                max(sl.id) AS id,
                so.company_id as company_id,
                sl.product_id as product_id,
                sl.name as product_name,
                pt.list_price as pro_sale_price,
                prop.value_float as pro_purchase_price,
                sum(product_uom_qty) as total_sale_quantity 
            FROM sale_order_line sl 
                JOIN sale_order so ON sl.order_id = so.id 
                --JOIN product_uom pu on sl.product_uom = pu.id
                JOIN product_product pp on sl.product_id = pp.id                   
                JOIN product_template pt on pp.product_tmpl_id=pt.id
                JOIN ir_property prop on prop.res_id = 'product.product,' || pp.id
            WHERE sl.state = 'sale' 
            GROUP BY sl.name,pt.list_price,sl.product_id,prop.value_float,so.company_id
            ORDER BY total_sale_quantity DESC
        )
        """ % self._table)
    
    