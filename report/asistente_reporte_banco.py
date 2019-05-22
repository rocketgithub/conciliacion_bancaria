# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import time

class AsistenteReporteBanco(models.TransientModel):
    _name = 'conciliacion_bancaria.asistente_reporte_banco'

    def _default_cuenta(self):
        if len(self.env.context.get('active_ids', [])) > 0:
            return self.env.context.get('active_ids')[0]
        else:
            return None

    cuenta_bancaria_id = fields.Many2one("account.account", string="Cuenta", required=True, default=_default_cuenta)
    mostrar_circulacion = fields.Boolean(string="Mostrar documentos en circulación")
    fecha_desde = fields.Date(string="Fecha Inicial", required=True, default=lambda self: time.strftime('%Y-%m-01'))
    fecha_hasta = fields.Date(string="Fecha Final", required=True, default=lambda self: time.strftime('%Y-%m-%d'))
    saldo_banco = fields.Float('Saldo banco')

    def print_report(self):
        active_ids = self.env.context.get('active_ids', [])
        data = {
             'ids': active_ids,
             'model': self.env.context.get('active_model', 'ir.ui.menu'),
             'form': self.read()[0]
        }
        return self.env['report'].get_action([], 'conciliacion_bancaria.reporte_banco', data=data)
