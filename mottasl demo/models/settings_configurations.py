from odoo import api, fields, models
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mottasl_api_key = fields.Char(
        string='Mottasl API Key',
        config_parameter='mottasl_api_key',
        help='Mottasl API Key related to your mottasl account',
        size=36,
        default= 'Enter your api key here',
        required=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ResConfigSettings, self).default_get(fields_list)
        res['mottasl_api_key'] = self.env['ir.config_parameter'].sudo().get_param('mottasl_api_key', default='')
        return res


