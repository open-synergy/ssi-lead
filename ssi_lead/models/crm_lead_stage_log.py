# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class CrmLeadStageLog(models.Model):  # pylint: disable=too-few-public-methods
    _name = "crm.lead.stage.log"
    _description = "CRM Lead Stage Log"
    _order = "date desc"

    lead_id = fields.Many2one(
        string="Lead",
        comodel_name="crm.lead",
        required=True,
        ondelete="cascade",
    )
    stage_id = fields.Many2one(
        string="Stage",
        comodel_name="crm.stage",
        required=True,
        ondelete="restrict",
    )
    date = fields.Datetime(
        string="Date",
        required=True,
        default=fields.Datetime.now,
    )
    user_id = fields.Many2one(
        string="Moved By",
        comodel_name="res.users",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.user,
        help="User who performed this stage transition.",
    )
