# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
from datetime import date
import logging

class ConciliacionBancariaConciliar(models.TransientModel):
    _name = "conciliacion_bancaria.conciliar"
    _description = "Conciliar con Banco"

    fecha = fields.Date(string="Fecha", required=True)

    def _check_fiscalyear_lock_date(self, move):
        self.ensure_one()

        lock_date = max(move.company_id.period_lock_date or date.min, move.company_id.fiscalyear_lock_date or date.min)
        if self.user_has_groups('account.group_account_manager'):
            lock_date = move.company_id.fiscalyear_lock_date

        if self.fecha <= (lock_date or date.min):
            if self.user_has_groups('account.group_account_manager'):
                message = _("You cannot add/modify entries prior to and inclusive of the lock date %s.") % format_date(self.env, lock_date)
            else:
                message = _("You cannot add/modify entries prior to and inclusive of the lock date %s. Check the company settings or ask someone with the 'Adviser' role") % format_date(self.env, lock_date)
            raise UserError(message)

        return True
    

    def conciliar(self):
        for rec in self:
            for line in self.env['account.move.line'].browse(self.env.context.get('active_ids', [])):
                if self._check_fiscalyear_lock_date(line.move_id):
                    self.env['conciliacion_bancaria.fecha'].create({
                        'move_id': line.id,
                        'fecha': rec.fecha
                    })

                    self.env['conciliacion_bancaria.pendiente'].conciliables(line.ref, line.account_id.id, line.debit - line.credit).unlink()

        return {'type': 'ir.actions.act_window_close'}

    def desconciliar(self):
        for rec in self:
            for line in self.env['account.move.line'].browse(self.env.context.get('active_ids', [])):
                if self._check_fiscalyear_lock_date(line.move_id):
                    conciliados = self.env['conciliacion_bancaria.fecha'].search([('move_id','=',line.id)]).unlink()

        return {'type': 'ir.actions.act_window_close'}
