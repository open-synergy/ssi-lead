# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class CrmLead(models.Model):  # pylint: disable=too-few-public-methods
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.data_requirement",
    ]
    _data_requirement_create_page = True
    _data_requirement_partner_field_name = "partner_id"
