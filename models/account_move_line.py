# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    conciliado_banco = fields.One2many("conciliacion_bancaria.fecha", "move_id", string="Conciliacion Linea")
    fecha_conciliacion = fields.Date(related="conciliado_banco.fecha", string="Fecha Conciliación")

class ConciliacionBancariaLinea(models.Model):
    """ Esto tiene que ser un registro aparte y no otra colummna de account.move.line
    para que se pueda conciliar y desconciliar aunque el movimiento ya este validado.
    """
    _name = "conciliacion_bancaria.fecha"
    _description = "Relaciona un apunte contable con la fecha que fue conciliado"

    move_id = fields.Many2one("account.move.line", string="Apunte", required=True)
    fecha = fields.Date(string="Fecha", required=True)

    _sql_constraints = [
        ("move_uniq", "unique (move_id)", "Ese apunte ya fue conciliado.")
    ]
