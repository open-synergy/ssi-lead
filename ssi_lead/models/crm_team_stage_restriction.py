# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmTeamStageRestriction(models.Model):
    """
    Represents a stage-transition restriction rule scoped to one sales
    team: leads belonging to that team may not move from
    `from_stage_id` to `to_stage_id`. Either field may be left empty to
    match "any stage" on that side of the transition, but at least one
    of the two must be set.
    """

    _name = "crm.team.stage_restriction"
    _description = "CRM Sales Team Stage Restriction"
    _order = "team_id, from_stage_id, to_stage_id"

    team_id = fields.Many2one(
        string="Sales Team",
        comodel_name="crm.team",
        required=True,
        ondelete="cascade",
        help="Sales team this stage restriction applies to.",
    )
    from_stage_id = fields.Many2one(
        string="From Stage",
        comodel_name="crm.stage",
        ondelete="restrict",
        help="Restriction applies when the lead is currently in this "
        "stage. Leave empty to match any origin stage.",
    )
    to_stage_id = fields.Many2one(
        string="To Stage",
        comodel_name="crm.stage",
        ondelete="restrict",
        help="Restriction applies when the lead is being moved into "
        "this stage. Leave empty to match any destination stage.",
    )
    role_ids = fields.Many2many(
        string="Allowed Roles",
        comodel_name="crm_team_role",
        relation="rel_crm_team_stage_restriction_2_role",
        column1="restriction_id",
        column2="role_id",
        required=True,
        help="Only users assigned to at least one of these roles within "
        "the sales team may perform this stage transition. At least one "
        "role is required.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_from_or_to_stage_required()
        records._check_role_required()
        return records

    @api.constrains("from_stage_id", "to_stage_id")
    def _check_from_or_to_stage_required(self):
        for record in self:
            if not record.from_stage_id and not record.to_stage_id:
                error_message = _(
                    """
Context: Configure sales team stage restriction
Database ID: %s
Problem: Both "From Stage" and "To Stage" are empty.
Solution: Fill in at least one of "From Stage" or "To Stage".
"""
                    % (record.id,)
                )
                raise ValidationError(error_message)

    @api.constrains("role_ids")
    def _check_role_required(self):
        for record in self:
            if not record.role_ids:
                error_message = _(
                    """
Context: Configure sales team stage restriction
Database ID: %s
Problem: No allowed role is set on this stage restriction.
Solution: Add at least one role under "Allowed Roles".
"""
                    % (record.id,)
                )
                raise ValidationError(error_message)
