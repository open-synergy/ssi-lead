# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CrmTeamRole(models.Model):
    """
    Represents a reusable role that can be assigned to sales team
    members, e.g. Presales, Account Executive. Used as a catalog of
    roles shared across all sales teams.
    """

    _name = "crm_team_role"
    _inherit = ["mixin.master_data"]
    _description = "CRM Sales Team Role"
