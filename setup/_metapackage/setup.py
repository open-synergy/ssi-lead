import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-lead",
    description="Meta package for open-synergy-ssi-lead Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_lead',
        'odoo14-addon-ssi_lead_project',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
