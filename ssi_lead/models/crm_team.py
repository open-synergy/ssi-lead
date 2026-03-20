# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class CrmTeam(models.Model):
    _name = "crm.team"
    _inherit = "crm.team"

    reminder_ids = fields.One2many(
        string="Reminders",
        comodel_name="crm.team.reminder",
        inverse_name="team_id",
    )
