# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.data_requirement",
    ]
    _data_requirement_create_page = True

    data_requirement_ids = fields.Many2many(
        relation="rel_lead_2_data_requirement",
        column1="lead_id",
        column2="data_requirement_id",
    )
