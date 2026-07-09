# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmTeamMemberRole(models.Model):
    """
    Represents the assignment of one or more users to a role within a
    sales team, e.g. Team X has 3 users playing the "Presales" role.
    Only users who are already members of the sales team may be
    assigned to a role in that team.
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
        help="Users filling this role. Must be members of the sales team.",
    )

    @api.constrains("user_ids", "team_id")
    def _check_user_team_membership(self):
        for record in self.sudo():
            if not record._check_user_team_membership_condition():
                error_message = _(
                    """
Context: Assign users to a sales team role
Database ID: %s
Problem: One or more users are not members of sales team "%s".
Solution: Only assign users who are members of the team (tab Members).
"""
                    % (record.id, record.team_id.name)
                )
                raise ValidationError(error_message)

    def _check_user_team_membership_condition(self):
        self.ensure_one()
        if not self.team_id or not self.user_ids:
            return True
        member_users = self.team_id.member_ids
        return all(user in member_users for user in self.user_ids)
