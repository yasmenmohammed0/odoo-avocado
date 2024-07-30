from odoo import models, fields, api

class CustomModel(models.Model):
    _name = 'custom.model'
    _description = 'Custom Model'

    name = fields.Char(string='Name')

    @api.model
    def get_installed_modules(self):
        installed_modules = self.env['ir.module.module'].search([('state', '=', 'installed')])
        module_names = installed_modules.mapped('name')
        return module_names
