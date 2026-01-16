# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Lead - Operating Unit",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_lead",
        "ssi_operating_unit_mixin",
    ],
    "data": [
        "security/res_groups/crm_lead.xml",
        "security/ir_rule/crm_lead.xml",
        "views/crm_lead.xml",
    ],
    "demo": [],
}
