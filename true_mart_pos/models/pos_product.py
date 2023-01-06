from odoo import models, fields, api, _

class PosProduct(models.Model):
    _inherit = 'product.template'
    
    product_min_qty = fields.Integer(string='Minimum Quantity of Product')
    has_mininmum_quantity = fields.Boolean(default='False', compute="_check_minimum_quantity")
    min_qty = fields.Integer('Reached Minimum Quantity of Product', readonly=False, compute='_compute_min_qty', store=True, track_visibility='always')
    
    
    @api.multi
    @api.depends('qty_available','product_min_qty')
    def _check_minimum_quantity(self):
        for product_obj in self:
            if product_obj.qty_available <= product_obj.product_min_qty:            
                    product_obj.has_mininmum_quantity=True
                  
    @api.depends('qty_available','product_min_qty')
    def _compute_min_qty(self):
        assign_min_val = 0
        for assign in self:
            if assign.qty_available <= assign.product_min_qty:
                assign_min_val = 1 
            else:
                assign_min_val = 0
                 
            assign.update({
                    'min_qty': assign_min_val,
                           }) 