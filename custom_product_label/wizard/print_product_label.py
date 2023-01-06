# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning

# TODO:  tests - try_report_action


class PrintProductLabel(models.TransientModel):
    _name = "print.product.label"

    @api.model
    def _get_products(self):
        res = []
        if self._context.get('active_model') == 'product.template':
            products = self.env[self._context.get('active_model')].browse(self._context.get('default_product_ids'))
            for product in products:
                label = self.env['product.label'].create({
                    'product_id': product.product_variant_id.id,
                })
                res.append(label.id)
        elif self._context.get('active_model') == 'product.product':
            products = self.env[self._context.get('active_model')].browse(self._context.get('default_product_ids'))
            for product in products:
                label = self.env['product.label'].create({
                    'product_id': product.id,
                })
                res.append(label.id)
        return res

    name = fields.Char('Name', default='Print Product Labels')
    label_ids = fields.One2many(
        comodel_name='product.label',
        inverse_name='wizard_id',
        string='Labels for Products',
        default=_get_products,
    )
    template = fields.Selection(
        selection=[('custom_product_label.report_product_label_A4_57x35', 'A4: 88 pcs on sheet, (4x22)')],
        string='Label template',
        default='custom_product_label.report_product_label_A4_57x35',
    )
    qty_per_product = fields.Integer(
        string='Label quantity per product',
        default=1,
    )

    @api.multi
    def action_print(self):
        """ Print labels
        """
        self.ensure_one()
        labels = self.label_ids.filtered('selected').mapped('id')
        if not labels:
            raise Warning(_('Nothing to print, set the quantity of labels in the table.'))
        return self.env.ref(self.template).with_context(discard_logo_check=True).report_action(labels)

    @api.multi
    def action_set_qty(self):
        self.ensure_one()
        self.label_ids.write({'qty': self.qty_per_product})

    @api.multi
    def action_restore_initial_qty(self):
        self.ensure_one()
        for label in self.label_ids:
            if label.qty_initial:
                label.update({'qty': label.qty_initial})

    @api.multi
    def action_back(self):
        self.ensure_one()
        return {'type': 'ir.actions.client', 'tag': 'history_back'}
