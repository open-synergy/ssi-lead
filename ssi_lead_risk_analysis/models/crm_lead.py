# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import api, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.risk_analysis",
    ]
    _risk_analysis_create_page = True
    _risk_analysis_partner_field_name = "partner_id"

    @api.onchange("partner_id")
    def onchange_risk_analysis_id(self):
        _super = super(CrmLead, self)
        _super.onchange_risk_analysis_id()
