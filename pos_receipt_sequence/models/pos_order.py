from odoo import models, fields, api, http
from odoo.http import request


class PosOrder(models.Model):
    _inherit = 'pos.order'

    receipt_sequence = fields.Char(
        string='Receipt Sequence',
        copy=False,
        readonly=True,
    )

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super().create_from_ui(orders, draft)
        if not res:
            return res
        records = {o.id: o.receipt_sequence for o in self.browse([r['id'] for r in res])}
        for r in res:
            r['receipt_sequence'] = records.get(r['id'])
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            frontend_bill_no = vals.get('bill_no') or vals.get('receipt_sequence')
            if frontend_bill_no:
                vals['receipt_sequence'] = frontend_bill_no
            elif not vals.get('receipt_sequence'):
                seq = self.env['ir.sequence'].next_by_code('pos.receipt.sequence')
                vals['receipt_sequence'] = seq
        orders = super().create(vals_list)
        return orders

    def _export_for_ui(self, order):
        result = super()._export_for_ui(order)
        result['receipt_sequence'] = order.receipt_sequence
        return result

    def _loader_params_pos_order(self):
        res = super()._loader_params_pos_order()
        if 'receipt_sequence' not in res['search_params']['fields']:
            res['search_params']['fields'].append('receipt_sequence')
        return res

class PosSequenceController(http.Controller):
    @http.route('/pos_sequence/latest', type='json', auth='public', methods=['POST'], website=False)
    def get_latest_sequence(self, **kwargs):
        config_id = kwargs.get('config_id')
        sequence = 'POS/00000'
        config = request.env['pos.config'].sudo().search([('id', '=', config_id)], limit=1)
        seq = config.sequence_id if config else None
        if seq:
            number_next = seq.number_next_actual
            padding = seq.padding or 5
            prefix = seq.prefix or ''
            sequence = f"{prefix}{str(number_next).zfill(padding)}"
        return {'receipt_sequence': sequence}
