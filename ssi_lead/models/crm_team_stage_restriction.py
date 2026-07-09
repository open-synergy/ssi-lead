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
