# -*- coding: utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
import xlrd
import base64

class ConciliacionBancariaAutomaticaPendiente(models.TransientModel):
    _name = 'conciliacion_bancaria.automatica.wizard.pendiente'

    conciliacion_automatica_id = fields.Many2one('conciliacion_bancaria.automatica.wizard', 'Encabezado')
    fecha = fields.Date('Fecha')
    tipo_documento = fields.Char('Tipo Doc.')
    numero_documento = fields.Char('No. Doc.')
    monto = fields.Char('Monto')
    tipo_movimiento = fields.Char('Tipo Mov.')

class ConciliacionBancariaAutomaticaWizard(models.TransientModel):
    _name = 'conciliacion_bancaria.automatica.wizard'

    fecha = fields.Date('Fecha Conciliación')
    account_id = fields.Many2one('account.account', 'Cuenta')
    archivo = fields.Binary('Archivo Excel')
    pendiente_ids = fields.One2many('conciliacion_bancaria.automatica.wizard.pendiente', 'conciliacion_automatica_id', string='Movimientos Bancarios no Encontrados')
    move_line_ids = fields.Many2many('account.move.line', string='Apuntes Contables sin Conciliar')

    def conciliar(self):
        workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.archivo))
        sheet = workbook.sheet_by_index(0)

        # En ese ciclo se construye el diccionario con la informacion del archivo de excel.
        linea_excel = {}
        for x in range(sheet.nrows):
            if x != 0:
                fecha = xlrd.xldate.xldate_as_datetime(sheet.cell(x, 0).value, workbook.datemode)
                tipo_documento = str(sheet.cell(x, 1).value)
                numero_documento = str(sheet.cell(x, 2).value)
                monto = float(sheet.cell(x, 3).value)
                tipo_movimiento = str(sheet.cell(x, 4).value)

                llave = numero_documento + '*' + str(self.account_id.id)
                linea_excel[llave] = {
                    'fecha': fecha.strftime("%Y-%m-%d"),
                    'tipo_documento': tipo_documento,
                    'monto': monto, 
                    'tipo_movimiento':tipo_movimiento,
                    'numero_documento': numero_documento,
                }

        apuntes = self.env['account.move.line'].search([('account_id', '=', self.account_id.id), ('conciliado_banco', '=', False)])
        apuntes_sin_conciliar = self.env['account.move.line']

        # Reviso si cada linea del account.move.line coincide con alguna llave del diccionario.
        # Si coincide, se hace conciliacion, de lo contrario se agrega la lineas que no hicieron match.
        for linea in apuntes:
            llave = linea.ref + '*' + str(linea.account_id.id)
            saldo = linea.debit - linea.credit
            if llave in linea_excel and linea_excel[llave]['monto'] == saldo:
                self.env['conciliacion_bancaria.fecha'].create({'move_id': linea.id, 'fecha': self.fecha})
                self.env['conciliacion_bancaria.pendiente'].conciliables(linea.ref, self.account_id.id, saldo).unlink()
                del linea_excel[llave]
            else:
                apuntes_sin_conciliar += linea

        lineas_sin_conciliar = []

        # El diccionario con las llaves que no fueron borradas las agrego al o2m, y si no existe la linea en el objeto de pendientes
        # de excel, agrego esa linea al objeto.
        for llave in linea_excel:
            lineas_sin_conciliar.append((0, 0, {
                'conciliacion_automatica_id': self.id,
                'fecha': linea_excel[llave]['fecha'],
                'tipo_documento': linea_excel[llave]['tipo_documento'],
                'numero_documento': linea_excel[llave]['numero_documento'],
                'monto': linea_excel[llave]['monto'],
                'tipo_movimiento': linea_excel[llave]['tipo_movimiento'],
            }))
            if not self.env['conciliacion_bancaria.pendiente'].conciliables(linea_excel[llave]['numero_documento'], self.account_id.id, linea_excel[llave]['monto']):
                self.env['conciliacion_bancaria.pendiente'].create({
                    'fecha': linea_excel[llave]['fecha'],
                    'account_id': self.account_id.id,
                    'tipo_documento': linea_excel[llave]['tipo_documento'],
                    'numero_documento': linea_excel[llave]['numero_documento'],
                    'monto': linea_excel[llave]['monto'],
                    'tipo_movimiento': linea_excel[llave]['tipo_movimiento']
                })

        self.write({
            'pendiente_ids': lineas_sin_conciliar,
            'move_line_ids': [(4, x.id) for x in apuntes_sin_conciliar],
        })

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'conciliacion_bancaria.automatica.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class ConciliacionAutomaticaLimpiarPendientesWizard(models.TransientModel):
    _name = 'conciliacion_bancaria.limpiar_pendientes.wizard'

    fecha = fields.Date('Fecha Conciliación')

    def conciliar(self):
        for linea_pendiente in self.env['conciliacion_bancaria.pendiente'].search([('id', 'in', self.env.context.get('active_ids', []))]):
            for move_line in self.env['account.move.line'].search([('account_id', '=', linea_pendiente.account_id.id), ('ref', '=', linea_pendiente.numero_documento), ('conciliado', '=', False)]):
                if linea_pendiente.monto == move_line.debit - move_line.credit:
                    linea_pendiente.unlink()
                    if not linea.conciliado:
                        self.env['conciliacion_bancaria.fecha'].create({'move_id': move_line.id, 'fecha': self.fecha})

        return {'type': 'ir.actions.act_window_close'}
