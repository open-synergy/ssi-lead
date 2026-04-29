# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class CrmTeamReminder(models.Model):  # pylint: disable=too-few-public-methods
    _name = "crm.team.reminder"
    _description = "CRM Sales Team Reminder"
    _order = "stage_id, days_on_stage, hours_on_stage"

    team_id = fields.Many2one(
        string="Sales Team",
        comodel_name="crm.team",
        required=True,
        ondelete="cascade",
    )
    stage_id = fields.Many2one(
        string="Stage",
        comodel_name="crm.stage",
        required=True,
        ondelete="restrict",
    )
    days_on_stage = fields.Integer(
        string="Days on Stage",
        default=0,
    )
    hours_on_stage = fields.Integer(
        string="Hours on Stage",
        default=0,
    )
    email_template_id = fields.Many2one(
        string="Email Template",
        comodel_name="mail.template",
        required=True,
        ondelete="restrict",
    )
    number_of_reminder = fields.Integer(
        string="Number of Reminder",
        default=1,
    )
    user_ids = fields.Many2many(
        string="Users",
        comodel_name="res.users",
        relation="rel_team_reminder_2_res_users",
        column1="reminder_id",
        column2="user_id",
        required=True,
    )
