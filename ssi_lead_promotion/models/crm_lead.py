# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmLead(models.Model):  # pylint: disable=too-few-public-methods
    """
    Lead extension that records the promotion codes claimed by the lead.

    The relation is informational only: it states which valid promotion
    codes the lead claims to hold, so the code entered on a portal form is
    validated by a relation instead of free text matching. It never
    redeems anything.
    """

    _name = "crm.lead"
    _inherit = [
        "crm.lead",
    ]

    promotion_code_ids = fields.Many2many(
        string="Promotion Codes",
        comodel_name="promotion_code",
        relation="crm_lead_promotion_code_rel",
        column1="lead_id",
        column2="promotion_code_id",
        domain=[("state", "=", "open")],
        help="Valid promotion codes claimed on this lead. This field is "
        "claim information only: it does not redeem the codes, does not "
        "create any promotion code usage, and does not deduct any amount.",
    )
