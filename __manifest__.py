# -*- encoding: utf-8 -*-

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
    'demo': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: