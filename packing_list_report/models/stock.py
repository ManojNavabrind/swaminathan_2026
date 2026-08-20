from odoo import api, fields, models,tools
from odoo.exceptions import UserError
from logging import getLogger


logger = getLogger(__name__)


class StockQuantPack(models.Model):
    _inherit='stock.quant.package'

    net_weight = fields.Float(string='Net Weight', compute='_compute_net_weight')
    gross_weight = fields.Float(string='Gross Weight', compute='_compute_gross_weight')

    @api.onchange('package_type_id')
    def onchange_package_type_id(self):
        if self.package_type_id:
            self.gross_weight = self.net_weight + self.package_type_id.base_weight

    @api.depends('package_type_id')
    def _compute_gross_weight(self):
        for rec in self:
            gross_weight = 0
            if rec.package_type_id and rec.package_type_id.base_weight > 0:
                gross_weight = rec.package_type_id.base_weight
            move_line_ids = self.env['stock.move.line'].sudo().search([
                ('result_package_id', '=', rec.id)
            ])
            if move_line_ids:
                gross_weight += sum(move_line_ids.mapped('weight'))
            rec.gross_weight = gross_weight

    def _compute_net_weight(self):
        for rec in self:
            total_weight = 0.0  # ✅ Initialize as float
            for q in rec.quant_ids:
                if q.product_uom_id.name == 'Piece':
                    total_weight += q.product_id.weight * q.quantity
                else:
                    total_weight = q.quantity
                # total_weight += (q.product_id.weight or 0.0) * (q.quantity or 0.0)
            rec.net_weight = total_weight
    # def _compute_net_weight(self):
    #     for rec in self:
    #         total_weight = ''
    #         for q in rec.quant_ids:
    #             total_weight += int(q.product_id.weight) * int(q.quantity)
    #         rec.net_weight = total_weight




class StockPicking(models.Model):
    _inherit="stock.picking"

    def write(self,vals):
        res=super(StockPicking,self).write(vals)
        packages = self.move_line_ids.mapped('result_package_id')
        for package in packages:
            pack = self.move_line_ids.filtered(lambda l: l.result_package_id == package)
            net_total = 0
            gross_weight = 0
            for rec in pack:
                if rec.product_uom_id.category_id.name != 'Unit':
                    net_total = net_total + rec.quantity
                if rec.secondary_uom.category_id.name != 'Unit':
                    net_total = net_total + rec.secondary_done
            gross_weight = net_total + package.package_type_id.base_weight
            package.net_weight = net_total
            package.gross_weight = gross_weight
        return res


class StockMove(models.Model):
    _inherit='stock.move'

    no_pcs = fields.Float(string='No.of Pcs')
    net_weight = fields.Float(string='Net Wgt', digits=(16,3))
    gross_weight = fields.Float(string='Gross Wgt')

    def compute_no_pcs(self):

        for rec1 in self:
            total_pcs = 0
            ids = self.env['stock.move.line'].search([('move_id', '=', rec1.id)])

            for rec in ids:

                total_pcs = total_pcs+ rec.no_pcs

            rec1.no_pcs = total_pcs

    @api.depends('move_line_ids', 'move_line_ids.net_weight')
    def _get_net_weight(self):
        for rec in self:
            if rec.product_uom.name == 'Kg':
                rec.net_weight = rec.quantity
            else:
                rec.net_weight = rec.quantity * rec.product_id.weight

    def _get_gross_weight(self):
        for rec in self:
            if rec.move_line_ids:
                for pack in rec.move_line_ids:
                    pack_weight = pack.result_package_id.package_type_id.base_weight
                rec.gross_weight = (rec.quantity * rec.product_id.weight) + pack_weight
            else:
                rec.gross_weight = (rec.quantity * rec.product_id.weight)

    def get_move_ids(self,o):
        package_gross_weights={}
        packages = o.move_line_ids.mapped('result_package_id')
        for package in packages:
            pack = o.move_line_ids.filtered(lambda l: l.result_package_id == package)
            total=0
            gross = 0
            for rec in pack:
                total = total+ rec.move_id.net_weight
            gross = total+package.package_type_id.base_weight
            package_gross_weights[package.name] = gross
        return package_gross_weights

class stockmoveline(models.Model):
    _inherit='stock.move.line'

    no_pcs = fields.Float(string='No.of Pcs')
    net_weight = fields.Float(string='Net Wgt')


    def write(self,vals):
        res=super(stockmoveline,self).write(vals)
        move_lines =self.move_id.picking_id
        packages = move_lines.move_line_ids.mapped('result_package_id')
        for package in packages:
            pack = move_lines.move_line_ids.filtered(lambda l: l.result_package_id == package)
            net_total = 0
            gross_weight = 0
            for rec in pack:
                if rec.product_uom_id.category_id.name != 'Unit':
                    net_total = net_total + rec.quantity
                if rec.secondary_uom.category_id.name != 'Unit':
                    net_total = net_total + rec.secondary_done

            gross_weight = net_total + package.package_type_id.base_weight
            package.net_weight = net_total
            package.gross_weight = gross_weight
        return res





