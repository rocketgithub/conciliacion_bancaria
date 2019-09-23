# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tipo_movimiento = fields.Selection([
            ('cheque','Cheque'),
            ('deposito','Depósito'),
            ('nota_credito','Nota de crédito'),
            ('nota_debito','Nota de débito')])

