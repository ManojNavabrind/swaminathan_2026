from odoo import models, fields


class MyWizard(models.TransientModel):
    _name = 'sale.report.wizard'

    customer = fields.Many2many('res.partner',string='Customer')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def sales_report(self):
            id_partner = []
            for rec in self.customer.ids:
                id_partner.append(rec)
            data = {'partner':id_partner,
                    'to_date': self.date_to,
                    'from_date': self.date_from,
                    }

            return self.env.ref('poompukar_sales_report.sales_report_pdf').report_action(self,data=data)

