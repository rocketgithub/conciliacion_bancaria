# -*- encoding: utf-8 -*-

from odoo import api, models
import datetime
import logging

class ReporteBancoResumido(models.AbstractModel):
    _name = 'report.conciliacion_bancaria.reporte_banco_resumido'

    def balance_final(self, datos):
#        self.env.cr.execute('select coalesce(sum(debit) - sum(credit), 0) as balance, coalesce(sum(amount_currency), 0) as balance_moneda from account_move_line l left join conciliacion_bancaria_fecha f on (l.id = f.move_id) where account_id = %s and fecha < %s', (datos.cuenta_bancaria_id.id, datos.fecha_hasta))
        self.env.cr.execute('select coalesce(sum(debit) - sum(credit), 0) as balance, coalesce(sum(amount_currency), 0) as balance_moneda from account_move_line where account_id = %s and date < %s', (datos.cuenta_bancaria_id.id, datos.fecha_hasta))
        return self.env.cr.dictfetchall()[0]

    def reporte(self, datos):
        cuenta = self.env['account.account'].browse(datos.cuenta_bancaria_id.id)
        encabezado = {}
        encabezado['cuenta'] = cuenta
        encabezado['moneda'] = cuenta.company_id.currency_id
        encabezado['fecha_desde'] = datetime.datetime.strftime(datos.fecha_desde, '%d/%m/%Y')
        encabezado['fecha_hasta'] = datetime.datetime.strftime(datos.fecha_hasta, '%d/%m/%Y')
        balance_final = self.balance_final(datos)['balance']
        resumen = {'ck_tr_pend_cambio': 0, 
                   'dep_transito': 0,
                   'deb_registrados_mas': 0,
                   'cred_registrados_mas': 0,
                   'saldo_conciliado_banco': datos.saldo_banco,
                   'balance_final': balance_final,
                   'ck_tr_pend_registro': 0,
                   'dep_pend_registro': 0,
                   'deb_pend_registro': 0,
                   'cred_pend_registro': 0,
                   'saldo_conciliado_compania': balance_final,
                  }

        lineas = {}
        lineas['cheque'] = []
        lineas['deposito'] = []
        lineas['nota_debito'] = []
        lineas['nota_credito'] = []
        move_lines = self.env['account.move.line'].search([('account_id', '=', datos.cuenta_bancaria_id.id), ('conciliado_banco','=',False), ('date','<=',datos.fecha_hasta)], order='date')
        for linea in move_lines:
            detalle = {
                'fecha': linea.date,
                'documento': linea.move_id.name if linea.move_id else '',
                'nombre': linea.partner_id.name or '',
                'concepto': (linea.ref if linea.ref else '') + (linea.name if linea.name else ''),
                'debito': linea.debit,
                'credito': linea.credit,
                'moneda': linea.company_id.currency_id,
            }
            if linea.journal_id.tipo_movimiento == 'cheque':
                lineas['cheque'].append(detalle)
                resumen['ck_tr_pend_cambio'] += linea.debit - linea.credit
            elif linea.journal_id.tipo_movimiento == 'deposito':
                lineas['deposito'].append(detalle)
                resumen['dep_transito'] += linea.debit - linea.credit
            elif linea.journal_id.tipo_movimiento == 'nota_debito':
                lineas['nota_debito'].append(detalle)
                resumen['deb_registrados_mas'] += linea.debit - linea.credit
            elif linea.journal_id.tipo_movimiento == 'nota_credito':
                lineas['nota_credito'].append(detalle)
                resumen['cred_registrados_mas'] += linea.debit - linea.credit

        resumen['ck_tr_pend_cambio'] = abs(resumen['ck_tr_pend_cambio'])
        resumen['dep_transito'] = abs(resumen['dep_transito'])
        resumen['deb_registrados_mas'] = abs(resumen['deb_registrados_mas'])
        resumen['cred_registrados_mas'] = abs(resumen['cred_registrados_mas'])

        resumen['saldo_conciliado_banco'] = resumen['saldo_conciliado_banco'] - resumen['ck_tr_pend_cambio'] + resumen['dep_transito'] + resumen['deb_registrados_mas'] - resumen['cred_registrados_mas']

        lineas['pendientes_cheque'] = []
        lineas['pendientes_deposito'] = []
        lineas['pendientes_nota_debito'] = []
        lineas['pendientes_nota_credito'] = []
        for movimiento in self.env['conciliacion_bancaria.pendientes_excel'].search([('account_id', '=', datos.cuenta_bancaria_id.id), ('fecha','<=',datos['fecha_hasta'])], order='fecha'):
            detalle = {
                'fecha': movimiento.fecha,
                'tipo_documento': movimiento.tipo_documento,
                'numero_documento': movimiento.numero_documento,
                'monto': movimiento.monto,
            }
            if movimiento.tipo_movimiento == 'cheque':
                lineas['pendientes_cheque'].append(detalle)
                resumen['ck_tr_pend_registro'] += movimiento.monto
            elif movimiento.tipo_movimiento == 'deposito':
                lineas['pendientes_deposito'].append(detalle)
                resumen['dep_pend_registro'] += movimiento.monto
            elif movimiento.tipo_movimiento == 'nota_debito':
                lineas['pendientes_nota_debito'].append(detalle)
                resumen['deb_pend_registro'] += movimiento.monto
            elif movimiento.tipo_movimiento == 'nota_credito':
                lineas['pendientes_nota_credito'].append(detalle)
                resumen['cred_pend_registro'] += movimiento.monto

        resumen['ck_tr_pend_registro'] = abs(resumen['ck_tr_pend_registro'])
        resumen['dep_pend_registro'] = abs(resumen['dep_pend_registro'])
        resumen['deb_pend_registro'] = abs(resumen['deb_pend_registro'])
        resumen['cred_pend_registro'] = abs(resumen['cred_pend_registro'])

        resumen['saldo_conciliado_compania'] = resumen['balance_final'] - resumen['ck_tr_pend_registro'] + resumen['dep_pend_registro'] + resumen['deb_pend_registro'] - resumen['cred_pend_registro']

        return {'encabezado': encabezado, 'lineas': lineas, 'resumen': resumen}


    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'moneda': docs[0].cuenta_bancaria_id.currency_id or self.env.user.company_id.currency_id,
            'reporte': self.reporte,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
