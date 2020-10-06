# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import logging

class Conciliar(models.TransientModel):
    _name = "conciliacion_bancaria.conciliar"
    _description = "Conciliar con banco"

    fecha = fields.Date(string="Fecha")

    @api.multi
    def conciliar(self):
        for rec in self:
            for line in self.env['account.move.line'].browse(self.env.context.get('active_ids', [])):
                lock_date = max(str(line.company_id.period_lock_date or '0000-00-00'), str(line.company_id.fiscalyear_lock_date or '0000-00-00'))
                if self.user_has_groups('account.group_account_manager'):
                    lock_date = str(line.company_id.fiscalyear_lock_date or '0000-00-00')

                if rec.fecha and lock_date < str(rec.fecha):
                    self.env['conciliacion_bancaria.fecha'].create({
                        'move_id': line.id,
                        'fecha': rec.fecha
                    })

                    for linea_pendiente in self.env['conciliacion_bancaria.pendientes_excel'].search([('account_id', '=', line.account_id.id), ('numero_documento', '=', line.ref)]):
                        if linea_pendiente.monto == line.debit - line.credit:
                            linea_pendiente.unlink()
                else:
                    raise UserError("La fecha ingresada es anterior a lo permitido en la configuración contable.")
        return {'type': 'ir.actions.act_window_close'}

    def desconciliar(self):
        for rec in self:
            for line in self.env['account.move.line'].browse(self.env.context.get('active_ids', [])):
                lock_date = max(str(line.company_id.period_lock_date or '0000-00-00'), str(line.company_id.fiscalyear_lock_date or '0000-00-00'))
                if self.user_has_groups('account.group_account_manager'):
                    lock_date = str(line.company_id.fiscalyear_lock_date or '0000-00-00')

                if line.conciliado_banco and lock_date < str(line.conciliado_banco.fecha):
                    conciliados = self.env['conciliacion_bancaria.fecha'].search([('move_id','=',line.id)]).unlink()
                else:
                    raise UserError("El movimiento no está conciliado ó la fecha conciliada es anterior a lo permitido en la configuración contable.")
        return {'type': 'ir.actions.act_window_close'}
