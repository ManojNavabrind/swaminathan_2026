{
    'name': 'Poompukar Sales Report',
    'description': 'Poompukar Sales Report',
    'summary': 'Poompukar Sales Report',
    'category': 'Inventory',
    'version': '17.0',
    'author': 'Navabrind IT Solutions',
    'company': 'Navabrind IT Solutions',
    'maintainer': 'Navabrind IT Solutions',
    'website': "",
    'depends': ['sale','stock'],
    'data': [
            #'views/views.xml',
            'wizard/wizard.xml',
            'security/ir.model.access.csv',
            'report/report.xml'
            ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
    },
    'license': 'LGPL-3',
}
