# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import time

class AsistenteReporteDisponibilidad(models.TransientModel):
    _name = 'conciliacion_bancaria.asistente_reporte_disponibilidad'

    cuentas_id = fields.Many2many('account.account','disponibilidad_cuentas_rel',string="Cuentas")
    mostrar_circulacion = fields.Boolean(string="Mostrar documentos en circulación")
    fecha_desde = fields.Date(string="Fecha Inicial", required=True, default=lambda self: time.strftime('%Y-%m-01'))
    fecha_hasta = fields.Date(string="Fecha Final", required=True, default=lambda self: time.strftime('%Y-%m-%d'))

    @api.multi
    def print_report(self):
        data = {
             'ids': [],
             'model': 'conciliacion_bancaria.asistente_reporte_disponibilidad',
             'form': self.read()[0]
        }
        return self.env.ref('conciliacion_bancaria.conciliacion_bancaria_action_reporte_disponibilidad').report_action(self, data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
