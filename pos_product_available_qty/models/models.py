from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    show_qtys = fields.Boolean(
        "Show Product Qtys", help="Show Product Qtys in POS", default=True
    )
