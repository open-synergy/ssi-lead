# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class CrmLead(models.Model):  # pylint: disable=too-few-public-methods
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.related_attachment",
    ]
    _related_attachment_create_page = True
