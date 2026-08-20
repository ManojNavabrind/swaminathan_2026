from odoo import models, fields, api,_


class StockMove(models.Model):
    _inherit = "stock.move"

    # 1. Add Display Type
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"),
    ], string="Display Type")

    # 2. Make Product Optional
    product_id = fields.Many2one('product.product', required=False)

    # 3. Make UoM Optional
    product_uom = fields.Many2one('uom.uom', required=False)

    # 4. Sequence
    sequence = fields.Integer(string='Sequence', default=10)

    # ---------------------------------------------------------
    # CRITICAL FIX 1: BYPASS MATH ENGINE
    # This prevents "precision_rounding must be positive" error
    # when UoM is False.
    # ---------------------------------------------------------
    def _set_quantity(self):
        # Only process standard moves. Skip Sections/Notes.
        # This stops Odoo from trying to round numbers without a UoM.
        normal_moves = self.filtered(lambda m: not m.display_type)
        return super(StockMove, normal_moves)._set_quantity()

    # ---------------------------------------------------------
    # CRITICAL FIX 2: CREATE OVERRIDE
    # This fixes "Invalid Operation" validation error.
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # We need a default location because DB requires it (NOT NULL constraint)
        default_loc = self.env.user.property_warehouse_id.lot_stock_id.id or 1

        for vals in vals_list:
            if vals.get('display_type'):
                # Force UoM to False.
                # Since we overrode _set_quantity above, this is now safe to do.
                vals.update({
                    'product_id': False,
                    # 'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'product_uom': False,
                    'product_uom_qty': 0,
                    'quantity': 0,
                    # Save the text
                    'name': vals.get('name') or vals.get('description_picking') or 'New Section',
                    # Satisfy DB Location constraints
                    'location_id': vals.get('location_id') or default_loc,
                    'location_dest_id': vals.get('location_dest_id') or default_loc,
                })

        return super().create(vals_list)

    # ---------------------------------------------------------
    # WORKFLOW BYPASS
    # Prevent stock reservation errors
    # ---------------------------------------------------------
    def _action_confirm(self, merge=True, merge_into=False):
        normal_moves = self.filtered(lambda m: not m.display_type)
        return super(StockMove, normal_moves)._action_confirm(merge=merge, merge_into=merge_into)

    def _action_assign(self):
        normal_moves = self.filtered(lambda m: not m.display_type)
        return super(StockMove, normal_moves)._action_assign()

    def _action_done(self, cancel_backorder=False):
        normal_moves = self.filtered(lambda m: not m.display_type)
        res = super(StockMove, normal_moves)._action_done(cancel_backorder=cancel_backorder)
        # Auto-complete sections
        self.filtered(lambda m: m.display_type).write({'state': 'done'})
        return res

    def action_show_details_wizard(self):

                """ Opens the Detailed Operations popup allowing generation for both Lots and Serials """

                self.ensure_one()

                # Fetch the standard form view layout template

                view = self.env.ref('stock.view_stock_move_operations')

                # Odoo explicit visibility computations

                show_lots_m2o = self.has_tracking != 'none' and (self.picking_type_id.use_existing_lots or self.state == 'done')

                show_lots_text = self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done'

                # FIX: Allow generation if tracking is 'serial' OR 'lot'

                is_trackable = self.has_tracking in ('serial', 'lot')

                can_create_lots = self.picking_type_id.use_create_lots and str(self.state) not in ('done', 'cancel')

                return {

                    'name': _('Detailed Operations'),

                    'type': 'ir.actions.act_window',

                    'view_mode': 'form',

                    'res_model': 'stock.move',

                    'views': [(view.id, 'form')],

                    'view_id': view.id,

                    'target': 'new',

                    'res_id': self.id,

                    'context': dict(

                        self.env.context,

                        picking_code=self.picking_code or (self.picking_id and self.picking_id.picking_type_code),

                        has_tracking=self.has_tracking,

                        show_lots_m2o=show_lots_m2o,

                        show_lots_text=show_lots_text,

                        # CHANGED HERE: Now allows 'lot' tracking configuration passes

                        show_assign_serial=is_trackable and can_create_lots,

                        show_next_serial=is_trackable and can_create_lots,

                        default_move_id=self.id,

                        default_product_id=self.product_id.id,

                        default_picking_id=self.picking_id.id,

                        default_location_id=self.location_id.id,

                        default_location_dest_id=self.location_dest_id.id,

                        default_company_id=self.company_id.id,

                    ),

                }

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):

        for picking in self:

            # remove section/note lines temporarily
            section_moves = picking.move_ids.filtered(lambda m: m.display_type)
            section_moves.write({'state': 'cancel'})

            # process normal moves
            for move in picking.move_ids.filtered(lambda m: not m.display_type):
                if not move.move_line_ids:
                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'picking_id': picking.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'qty_done': move.product_uom_qty,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                    })
                else:
                    for line in move.move_line_ids:
                        if line.qty_done == 0:
                            line.qty_done = move.product_uom_qty

        return super().button_validate()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # 1. Run the standard confirmation (creates product moves)
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            # 2. Find the Delivery (Picking) that was just created
            pickings = order.picking_ids.filtered(lambda p: p.state != 'cancel')
            if not pickings:
                continue

            # Use the first picking found
            picking = pickings[0]

            # 3. Look for Sections/Notes in the Sales Order lines
            for line in order.order_line.filtered(lambda l: l.display_type):
                # 4. Manually create the "BOX A / BOX B" line in the Delivery
                self.env['stock.move'].create({
                    'name': line.name,
                    'product_id': False,
                    'product_uom': False,
                    'product_uom_qty': 0,
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'display_type': line.display_type,
                    'sequence': line.sequence,  # Keeps the order correct
                    'sale_line_id': line.id,  # Links back to Sale Order
                })
        return res
