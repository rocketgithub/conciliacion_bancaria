# -*- encoding: utf-8 -*-

#
# Este es el modulo de conciliación bancaria
#
# Status 1.0 - tested on Open ERP 7.0
#

{
    'name' : 'conciliacion_bancaria',
    'version' : '1.0',
    'category': 'Custom',
    'description': """Manejo de conciliación bancaria""",
    'author': 'Rodrigo Fernandez',
    'website': 'http://solucionesprisma.com/',
    'depends' : [ 'account', 'l10n_gt' ],
    'data' : [
        'views/account_move_line.xml',
        'views/reporte_banco.xml',
        'wizard/conciliar.xml',
        'views/conciliacion_automatica.xml',
        #'views/reporte_disponibilidad_resumen.xml',
        'wizard/conciliacion_automatica.xml',
        'security/ir.model.access.csv',
        'views/report.xml',

    ],
    'installable': True,
}
