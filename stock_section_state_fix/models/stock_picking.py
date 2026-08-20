from collections import defaultdict

from odoo import api, models, _
from odoo.tools import float_compare, format_date


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends(
        'move_ids.state',
        'move_ids.product_uom_qty',
        'move_ids.quantity',
        'move_ids.forecast_availability',
        'move_ids.forecast_expected_date',
    )
    def _compute_products_availability(self):
        pickings = self.filtered(
            lambda p: p.state in ('waiting', 'confirmed', 'assigned')
            and p.picking_type_code == 'outgoing'
        )

        pickings.products_availability_state = 'available'
        pickings.products_availability = _('Available')

        other_pickings = self - pickings
        other_pickings.products_availability = False
        other_pickings.products_availability_state = False

        # Ignore Section / Note moves
        all_moves = pickings.move_ids.filtered(lambda m: not m.display_type)

        all_moves._fields['forecast_availability'].compute_value(all_moves)

        for picking in pickings:

            # Ignore Section / Note moves
            normal_moves = picking.move_ids.filtered(lambda m: not m.display_type)

            if any(
                float_compare(
                    move.forecast_availability,
                    0 if move.state == 'draft' else move.product_qty,
                    precision_rounding=move.product_id.uom_id.rounding,
                ) == -1
                for move in normal_moves
            ):
                picking.products_availability = _('Not Available')
                picking.products_availability_state = 'late'
            else:
                forecast_date = max(
                    normal_moves.filtered('forecast_expected_date').mapped('forecast_expected_date'),
                    default=False,
                )

                if forecast_date:
                    picking.products_availability = _(
                        'Exp %s',
                        format_date(self.env, forecast_date),
                    )
                    picking.products_availability_state = (
                        'late'
                        if picking.scheduled_date and picking.scheduled_date < forecast_date
                        else 'expected'
                    )

        #method for computing state

    @api.depends(
        'move_type',
        'move_ids.state',
        'move_ids.picked',
        'move_ids.scrapped',
        'move_ids.product_uom_qty',
    )
    def _compute_state(self):
        picking_moves_state_map = defaultdict(dict)
        picking_move_lines = defaultdict(set)

        # Ignore section/note moves
        moves = self.env['stock.move'].search([
            ('picking_id', 'in', self.ids),
            ('display_type', '=', False),
        ])

        for move in moves:
            picking_id = move.picking_id
            move_state = move.state

            picking_moves_state_map[picking_id.id].update({
                'any_draft': picking_moves_state_map[picking_id.id].get('any_draft',
                                                                        False) or move_state == 'draft',
                'all_cancel': picking_moves_state_map[picking_id.id].get('all_cancel',
                                                                         True) and move_state == 'cancel',
                'all_cancel_done': picking_moves_state_map[picking_id.id].get('all_cancel_done',
                                                                              True) and move_state in ('cancel',
                                                                                                       'done'),
                'all_done_are_scrapped': picking_moves_state_map[picking_id.id].get('all_done_are_scrapped',
                                                                                    True) and (
                                             move.scrapped if move_state == 'done' else True),
                'any_cancel_and_not_scrapped': picking_moves_state_map[picking_id.id].get(
                    'any_cancel_and_not_scrapped', False) or (move_state == 'cancel' and not move.scrapped),
            })

            picking_move_lines[picking_id.id].add(move.id)

        for picking in self:
            data = picking_moves_state_map[picking.id]

            if not data or data['any_draft']:
                picking.state = 'draft'

            elif data['all_cancel']:
                picking.state = 'cancel'

            elif data['all_cancel_done']:
                if data['all_done_are_scrapped'] and data['any_cancel_and_not_scrapped']:
                    picking.state = 'cancel'
                else:
                    picking.state = 'done'

            else:
                normal_moves = picking.move_ids.filtered(lambda m: not m.display_type)

                if picking.location_id.should_bypass_reservation() and all(
                        m.procure_method == 'make_to_stock' for m in normal_moves):
                    picking.state = 'assigned'
                else:
                    relevant = normal_moves._get_relevant_state_among_moves()
                    picking.state = 'assigned' if relevant == 'partially_available' else relevant
