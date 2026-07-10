# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmTeamMemberRole(models.Model):
    """
    Represents the assignment of one or more users to a role within a
    sales team, e.g. Team X has 3 users playing the "Presales" role.
    """

    _name = "crm.team.member_role"
    _description = "CRM Sales Team Member Role"
    _order = "team_id, role_id"

    team_id = fields.Many2one(
        string="Sales Team",
        comodel_name="crm.team",
        required=True,
        ondelete="cascade",
        help="Sales team this role assignment belongs to.",
    )
    role_id = fields.Many2one(
        string="Role",
        comodel_name="crm_team_role",
        required=True,
        ondelete="restrict",
        help="Role played by the assigned users within the sales team.",
    )
    user_ids = fields.Many2many(
        string="Users",
        comodel_name="res.users",
        relation="rel_crm_team_member_role_2_res_users",
        column1="member_role_id",
        column2="user_id",
        required=True,
        help="Users filling this role.",
    )
