# -*- encoding: utf-8 -*-

from odoo import api, models
import logging

class ReporteBanco(models.AbstractModel):
    _name = 'report.conciliacion_bancaria.reporte_banco'

    def lineas(self, conciliadas, datos):
        lineas = []

        query = None
        if conciliadas:
            # query = [('conciliado_banco','!=',False), ('account_id','=',datos['cuenta_bancaria_id'][0]), ('conciliado_banco.fecha','>=',datos['fecha_desde']), ('conciliado_banco.fecha','<=',datos['fecha_hasta'])]
            query = [('conciliado_banco','!=',False), ('account_id','in',datos['cuentas_id']), ('conciliado_banco.fecha','>=',datos['fecha_desde']), ('conciliado_banco.fecha','<=',datos['fecha_hasta'])]
        else:
            # query = [('conciliado_banco','=',False), ('account_id','=',datos['cuenta_bancaria_id'][0])]
            query = [('conciliado_banco','=',False), ('account_id','in',datos['cuentas_id'])]
        for linea in self.env['account.move.line'].search(query, order='date'):
            detalle = {
                'id_cuenta': linea.account_id.id,
                'codigo_cuenta': linea.account_id.code,
                'cuenta': linea.account_id.name,
                'fecha': linea.date,
                'documento': linea.move_id.name if linea.move_id else '',
                'nombre': linea.partner_id.name or '',
                'concepto': (linea.ref if linea.ref else '') + (linea.name if linea.name else ''),
                'debito': linea.debit,
                'credito': linea.credit,
                'balance': 0,
                'saldo_final':0,
                'tipo': '',
                'moneda': linea.company_id.currency_id,
                'conciliado_banco': linea.conciliado_banco
            }

            if linea.amount_currency:
                detalle['moneda'] = linea.currency_id
                if linea.amount_currency > 0:
                    detalle['debito'] = linea.amount_currency
                else:
                    detalle['credito'] = -1 * linea.amount_currency

            lineas.append(detalle)

        # balance_inicial = self.balance_inicial(datos)

        # if balance_inicial['balance_moneda']:
        #     balance = balance_inicial['balance_moneda']
        # elif balance_inicial['balance']:
        #     balance = balance_inicial['balance']
        # else:
        #     balance = 0
        #
        # for linea in lineas:
        #
        #     balance = balance + linea['debito'] - linea['credito']
        #     linea['balance'] = balance

        cuentas_agrupadas = {}
        llave = 'codigo_cuenta'
        for l in lineas:
            if l[llave] not in cuentas_agrupadas:
                cuentas_agrupadas[l[llave]] = {'codigo': l[llave],'cuenta':l['cuenta'] ,'id_cuenta': l['id_cuenta'],'movimientos':[], 'saldo_inicial': 0, 'saldo_final':0 }
            cuentas_agrupadas[l[llave]]['movimientos'].append(l)

        for cuenta in cuentas_agrupadas.values():
            cuenta['saldo_final'] = self.saldo_final(cuenta['id_cuenta'],datos)['saldo_final']

        lineas = cuentas_agrupadas.values()

        return lineas

    # def balance_inicial(self, datos):
    #     self.env.cr.execute('select coalesce(sum(debit) - sum(credit), 0) as balance, coalesce(sum(amount_currency), 0) as balance_moneda from account_move_line l left join conciliacion_bancaria_fecha f on (l.id = f.move_id) where account_id = %s and fecha < %s', (datos['cuenta_bancaria_id'][0], datos['fecha_desde']))
    #     return self.env.cr.dictfetchall()[0]

    def saldo_final(self, cuenta,datos):
        self.env.cr.execute('select coalesce(sum(debit) - sum(credit), 0) as saldo_final, coalesce(sum(amount_currency), 0) as balance_moneda from account_move_line l left join conciliacion_bancaria_fecha f on (l.id = f.move_id) where account_id = %s and fecha < %s', (cuenta, datos['fecha_hasta']))
        return self.env.cr.dictfetchall()[0]

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            # 'moneda': docs[0].cuenta_bancaria_id.currency_id or self.env.user.company_id.currency_id,
            'lineas': self.lineas,
            # 'balance_inicial': self.balance_inicial(data['form']),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
