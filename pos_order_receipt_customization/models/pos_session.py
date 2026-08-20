from odoo import models, fields


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()

        result["search_params"]["fields"] += [
            "city",
            "zip",
            "phone2",
            "phone3",
            "vat"
        ]

        return result

