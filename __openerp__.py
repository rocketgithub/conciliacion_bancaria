# -*- encoding: utf-8 -*-

#
# Este es el modulo de conciliación bancaria
#
# Status 1.0 - tested on Odoo 9.0
#

{
    'name' : 'Conciliación Bancaria',
    'version' : '1.0',
    'category': 'Custom',
    'description': """Manejo de conciliación bancaria""",
    'author': 'Rodrigo Fernandez',
    'website': 'http://solucionesprisma.com/',
    'depends' : [ 'l10n_gt_extra' ],
    'data' : [
        'views/account_move_line.xml',
        'views/report.xml',
        'views/reporte_banco.xml',
        'wizard/conciliar.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'certificate': '',
}
