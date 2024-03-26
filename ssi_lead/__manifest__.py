# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Lead Enhancement",
    "version": "14.0.2.1.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "crm",
        "ssi_master_data_mixin",
        "ssi_sequence_mixin",
        "ssi_product",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "views/crm_lead_views.xml",
    ],
    "demo": [],
}
