from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        res = super()._loader_params_pos_payment_method()
        res["search_params"]["fields"].extend(["journal_id"])
        return res

    def _get_pos_ui_pos_payment_method(self, params):
        payments = self.env['pos.payment.method'].search_read(**params['search_params'])
        for payment in payments:
            if payment['journal_id']:
                journal = self.env['account.journal'].search_read(
                    domain=[('id', '=', payment['journal_id'][0])],
                    fields=['name', 'pos_method_type', 'decimal_rounding']
                )
                payment['journal'] = journal[0]
            del payment['journal_id']
        return payments
