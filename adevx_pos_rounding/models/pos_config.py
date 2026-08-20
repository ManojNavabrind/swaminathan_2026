from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    rounding = fields.Boolean(string='Price Rounding')
    rounding_type = fields.Selection(
        selection=[
            ('rounding_up', 'Rounding Up'),
            ('rounding_down', 'Rounding Down'),
            ('rounding_up_down', 'Rounding Up and Down')],
        default='rounding_up_down',
        help='1) * Rounding up: \n'
             'Rule: 2.5 to 4.9999 will  +5.0 \n'
             '2) * Rounding down: \n'
             'Rule: 0.1 to 2.4999 become 0.0\n'
             '3) * Rounding up and down \n'
             'Rule 1: 0.1 to 2.4999 become 0.0 \n'
             'Rule 2: 2.5 to 4.9999 will  +5.0'
    )
    rounding_factor = fields.Float(string='Rounding Factor', default=1)
    decimal_places = fields.Integer(string='Decimal Places', default=0)
    # Automatic
    rounding_automatic = fields.Boolean(
        string='Rounding Automatic',
        help='When cashier go to Payment Screen, POS auto rounding')
    rounding_automatic_type = fields.Selection(
        selection=[
            ('rounding_by_decimal_journal', 'By Decimal Rounding of Journal'),
            ('rounding_integer', 'Rounding to Integer'),
            ('rounding_up', 'Rounding Up'),
            ('rounding_down', 'Rounding Down'),
            ('rounding_up_down', 'Rounding Up and Down')],
        default='rounding_integer',
        help='1) * By Decimal Rounding of Payment Method [Rounding Amount]\n'
             '2) * Rounding to Integer: \n'
             'Rule 1: 0.1 to 0.4999 become 0.0 \n'
             'Rule 2: 0.5 to 0.9999 will  +1.0 \n'
             '3) * Rounding up: \n'
             'Rule: 2.5 to 4.9999 will  +5.0 \n'
             '4) * Rounding down: \n'
             'Rule: 0.1 to 2.4999 become 0.0\n'
             '5) * Rounding up and down \n'
             'Rule 1: 0.1 to 2.4999 become 0.0 \n'
             'Rule 2: 2.5 to 4.9999 will  +5.0'
    )
    rounding_automatic_factor = fields.Float(string='Rounding Automatic Factor', default=5)
