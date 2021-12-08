# -*- encoding: utf-8 -*-

from odoo import models, fields, api
import logging

class AccountMove(models.Model):
    _inherit = "account.move"

    no_conciliar_con_banco = fields.Boolean(string='No conciliar con banco', default=False)
