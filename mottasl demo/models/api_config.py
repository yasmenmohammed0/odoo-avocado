from odoo import api, models,fields
class ApiConf(models.Model):
    _name = 'api.conf'
    _description = "api configuration"
    apiKey=fields.Char(string='API Key',required=True)