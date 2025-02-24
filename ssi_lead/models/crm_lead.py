# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import api, fields, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.sequence",
    ]

    name = fields.Char(
        string="Opportunity",
        default="/",
        required=True,
        index=True,
        copy=False,
    )
    allowed_contact_contractor_ids = fields.Many2many(
        string="Allowed Contractor's Contact",
        comodel_name="res.partner",
        compute="_compute_allowed_contact_contractor_ids",
        store=False,
    )
    contractor_id = fields.Many2one(
        string="Contractor",
        comodel_name="res.partner",
        domain=[
            ("parent_id", "=", False),
        ],
    )
    contact_contractor_id = fields.Many2one(
        string="Contact's Contact",
        comodel_name="res.partner",
        required=False,
    )
    reference_ids = fields.Many2many(
        string="References",
        comodel_name="res.partner",
        relation="rel_lead_reference_2_partner",
        column1="lead_id",
        column2="partner_id",
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
    )
    product_ids = fields.Many2many(
        string="Products",
        comodel_name="product.product",
        relation="rel_lead_2_product",
        column1="lead_id",
        column2="product_id",
    )

    @api.depends(
        "contractor_id",
    )
    def _compute_allowed_contact_contractor_ids(self):
        Partner = self.env["res.partner"]
        for record in self:
            result = []
            if record.contractor_id:
                criteria = [
                    ("commercial_partner_id", "=", record.contractor_id.id),
                    ("id", "!=", record.contractor_id.id),
                    ("type", "=", "contact"),
                ]
                result = Partner.search(criteria).ids
            record.allowed_contact_contractor_ids = result

    @api.model
    def create(self, values):
        _super = super(CrmLead, self)
        result = _super.create(values)
        try:
            result._create_sequence()
        except Exception:
            pass
        return result
