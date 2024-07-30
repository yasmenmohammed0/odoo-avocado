import json
import logging
from datetime import date, datetime

import requests

from odoo import models, api

_logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_api_key(self):
        api_config = self.env['api.configuration'].search([], limit=1)
        return api_config.api_key if api_config else None

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("Creating new sales orders with values: %s", vals_list)
        records = super(SaleOrder, self).create(vals_list)
        self._send_order_data(records, event='Sales Order Created')
        return records

    def write(self, vals):
        _logger.info("Updating sales orders with values: %s", vals)
        result = super(SaleOrder, self).write(vals)
        self._send_order_data(self, event='Sales Order Updated')
        return result

    def unlink(self):
        _logger.info("Deleting sales orders with ids: %s", self.ids)
        records = self.read(['id', 'partner_id'])  # Read necessary data before deletion
        result = super(SaleOrder, self).unlink()
        self._send_delete_action(records)
        return result

    def _send_delete_action(self, records):
        param_obj = self.env['ir.config_parameter']
        mottasl_api_key = param_obj.get_param('mottasl_api_key')

        if not mottasl_api_key:
            _logger.error("API Key not configured. Unable to send delete action.")
            return

        for record in records:
            partner = self.env['res.partner'].browse(record['partner_id'][0])
            customer_phone = partner.phone or partner.mobile or 'N/A'

            url = f'https://clients.twerlo.com/odoo-events?api_key={mottasl_api_key}'

            delete_data = {
                'id': record['id'],
                'event': 'order.delete',
                'customer_phone': customer_phone,
                'deletion_date': datetime.now().isoformat(),
            }

            _logger.info("Sending delete action data to endpoint: %s", url)
            try:
                json_data = json.dumps(delete_data, cls=DateTimeEncoder)
                response = requests.post(
                    url,
                    data=json_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=60  # Increase the timeout to 60 seconds
                )
                response.raise_for_status()
                _logger.info("Successfully sent delete action data. Response: %s", response.text)
            except requests.exceptions.RequestException as e:
                _logger.error("Failed to send delete action data: %s", e)

    def _send_order_data(self, records, event):
        param_obj = self.env['ir.config_parameter']
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        mottasl_api_key = param_obj.get_param('mottasl_api_key')

        if not mottasl_api_key:
            _logger.error("API Key not configured. Unable to send order data.")
            return

        for record in records:
            partner = record.partner_id
            additional_data = {
                'customer_phone': partner.phone,
                'event': event,
                'order_url': f'{base_url}/web#id={record.id}&view_type=form&model=sale.order'
                # Add other necessary fields here
            }

            _logger.info("Extracted partner data: %s", additional_data)

            record_data = record.read()[0]

            record_data.update(additional_data)  # Merge additional data into the record data

            _logger.info("Final record data to be sent: %s", record_data)

            url = f'https://clients.twerlo.com/odoo-events?api_key={mottasl_api_key}'

            _logger.info("Sending order data to endpoint: %s", url)
            try:
                json_data = json.dumps(record_data, cls=DateTimeEncoder)

                response = requests.post(
                    url,
                    data=json_data,  # Use json parameter for automatic JSON serialization
                    headers={'Content-Type': 'application/json', 'event-name': event},
                    timeout=60  # Increase the timeout to 60 seconds
                )
                response.raise_for_status()
                _logger.info("Successfully sent order data. Response: %s", response.text)
            except requests.exceptions.RequestException as e:
                _logger.error("Failed to send order data: %s", e)
