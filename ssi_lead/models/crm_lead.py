# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import api, fields, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.sequence",
    ]

    name = fields.Char(
        string="Opportunity",
        default="/",
        required=True,
        index=True,
        copy=False,
    )

    @api.model
    def create(self, values):
        _super = super(CrmLead, self)
        result = _super.create(values)
        try:
            result._create_sequence()
        except Exception:
            pass
        return result
