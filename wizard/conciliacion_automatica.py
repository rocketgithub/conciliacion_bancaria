# -*- coding: utf-8 -*-

from odoo import api, models, fields
import logging
import datetime
import xlrd
import base64

class ConciliacionAutomaticaExcel(models.TransientModel):
    _name = 'conciliacion_bancaria.excel'

    conciliacion_automatica_id = fields.Many2one('conciliacion_bancaria.wizard', 'Conciliacion Automatica ID')
    fecha = fields.Date('Fecha')
    tipo_documento = fields.Char('Tipo doc.')
    numero_documento = fields.Char('No. doc.')
    monto = fields.Char('Monto')

class ConciliacionAutomaticaWizard(models.TransientModel):
    _name = 'conciliacion_bancaria.wizard'

    fecha = fields.Date('Fecha conciliación')
    account_id = fields.Many2one('account.account', 'Cuenta')
    archivo = fields.Binary('Archivo excel')
    move_line_ids = fields.Many2many('account.move.line', string='Apuntes contables')
    excel_ids = fields.One2many('conciliacion_bancaria.excel', 'conciliacion_automatica_id', string='Detalle excel')

    @api.multi
    def conciliar(self):
        workbook = xlrd.open_workbook(file_contents = base64.decodestring(self.archivo))
        sheet = workbook.sheet_by_index(0)

        dict = {}
        #En ese ciclo se construye el diccionario con la informacion del archivo de excel.
        for x in xrange(sheet.nrows):
            if x != 0:
                fecha = datetime.datetime(*xlrd.xldate_as_tuple(sheet.cell(x, 0).value, workbook.datemode))
                fecha = datetime.datetime.strftime(fecha, "%Y-%m-%d")
                tipo_documento = sheet.cell(x, 1).value
                numero_documento = sheet.cell(x, 2).value
                llave = str(fecha) + '*' + str(numero_documento)
                dict[llave] = {}
                dict[llave]['tipo_documento'] = sheet.cell(x, 1).value
                dict[llave]['monto'] = float(sheet.cell(x, 3).value)
        logging.getLogger('DICCIONARIO').warn(dict)
        lineas = self.env['account.move.line'].search([('account_id', '=', self.account_id.id)])
        m2m_ids = []
        pendientes_excel_obj = self.env['conciliacion_bancaria.pendientes_excel']
        #Reviso si cada linea del account.move.line coincide con alguna llave del diccionario.
        #Si coincide, se hace conciliacion, de lo contrario se agrega la linea al m2m de lineas que no hicieron match.
        for linea in lineas:
            llave = str(linea.date) + '*' + str(linea.ref)
            logging.getLogger('LLAVE').warn(llave)
            saldo = linea.debit - linea.credit
            if llave in dict and dict[llave]['monto'] == saldo and not linea.conciliado_banco:
                self.env['conciliacion_bancaria.fecha'].create({'move_id': linea.id, 'fecha': self.fecha})
                dict.pop(llave)
                #Reviso si la linea a conciliar existe en los pendientes de excel. Si existe, la borro.
                excel_id = pendientes_excel_obj._existe_registro(linea.date, self.account_id.id, linea.ref)
                if excel_id:
                    excel_obj = self.env['conciliacion_bancaria.pendientes_excel'].search([('id', '=', excel_id)])
                    excel_obj.unlink()
            else:
                m2m_ids.append((4, linea.id))

        o2m_ids = []
        #El diccionario con las llaves que no fueron borradas las agrego al o2m, y si no existe la linea en el objeto de pendientes
        #de excel, agrego esa linea al objeto.
        logging.warn('HOLA')
        for llave in dict:
            campos = llave.split('*')
            logging.warn(campos)
            o2m_ids.append((0, 0, {'conciliacion_automatica_id': self.id, 'fecha':campos[0], 'tipo_documento': dict[llave]['tipo_documento'], 'numero_documento':campos[1], 'monto': dict[llave]['monto']}))
            if not pendientes_excel_obj._existe_registro(campos[0], self.account_id.id, campos[1]):
                pendientes_excel_obj.create({'fecha': campos[0], 'account_id': self.account_id.id, 'tipo_documento': dict[llave]['tipo_documento'], 'numero_documento': campos[1], 'monto': dict[llave]['monto']})

        actualizar = {}
        if o2m_ids:
            actualizar['excel_ids'] = o2m_ids
        if m2m_ids:
            actualizar['move_line_ids'] = m2m_ids

        if len(actualizar) > 0:
            self.write(actualizar)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'conciliacion_bancaria.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
