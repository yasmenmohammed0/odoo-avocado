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


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _get_api_key(self):
        api_config = self.env['api.configuration'].search([], limit=1)
        return api_config.api_key if api_config else None

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("Creating new invoices with values: %s", vals_list)
        records = super(AccountMove, self).create(vals_list)
        self._send_invoice_data(records, event='invoice.create')
        return records

    def write(self, vals):
        _logger.info("Updating invoices with values: %s", vals)
        result = super(AccountMove, self).write(vals)
        self._send_invoice_data(self, event='invoice.update')
        return result

    def unlink(self):
        _logger.info("Deleting invoices with ids: %s", self.ids)
        records = self.read(['id', 'move_type', 'partner_id'])  # Read necessary data before deletion
        result = super(AccountMove, self).unlink()
        self._send_delete_action(records)
        return result

    def _send_delete_action(self, records):
        param_obj = self.env['ir.config_parameter']
        mottasl_api_key = param_obj.get_param('mottasl_api_key')

        if not mottasl_api_key:
            _logger.error("API Key not configured. Unable to send delete action.")
            return

        for record in records:
            if record['move_type'] == 'out_invoice':  # Check if it's a customer invoice
                partner = self.env['res.partner'].browse(record['partner_id'][0])
                customer_phone = partner.phone or partner.mobile or 'N/A'

                url = f'https://clients.twerlo.com/odoo-events?api_key={mottasl_api_key}'

                delete_data = {
                    'id': record['id'],
                    'event': 'invoice.delete',
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

    def _send_invoice_data(self, records, event):
        param_obj = self.env['ir.config_parameter']
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        mottasl_api_key = param_obj.get_param('mottasl_api_key')

        if not mottasl_api_key:
            _logger.error("API Key not configured. Unable to send invoice data.")
            return

        for record in records:
            if record.move_type == 'out_invoice':  # Check if it's a customer invoice and status is "posted"
                partner = record.partner_id
                additional_data = {
                    'customer_phone': partner.phone,
                    'event': event,
                    'invoice_pdf_url': f'{base_url}/report/pdf/account.report_invoice_with_payments/{record.id}'
                    # Add the event name
                    # Add other necessary fields here
                }

                _logger.info("Extracted partner data: %s", additional_data)

                record_data = record.read()[0]
                if 'invoice_pdf_report_file' in record_data:
                    del record_data['invoice_pdf_report_file']  # Remove the key if it exists

                record_data.update(additional_data)  # Merge additional data into the record data

                _logger.info("Final record data to be sent: %s", record_data)

                url = f'https://clients.twerlo.com/odoo-events?api_key={mottasl_api_key}'

                _logger.info("Sending invoice data to endpoint: %s", url)
                try:
                    json_data = json.dumps(record_data, cls=DateTimeEncoder)

                    response = requests.post(
                        url,
                        data=json_data,  # Use json parameter for automatic JSON serialization
                        headers={'Content-Type': 'application/json', 'event-name': event},
                        timeout=60  # Increase the timeout to 60 seconds
                    )
                    response.raise_for_status()
                    _logger.info("Successfully sent invoice data. Response: %s", response.text)
                except requests.exceptions.RequestException as e:
                    _logger.error("Failed to send invoice data: %s", e)
            else:
                _logger.info("Skipping record %s because status is not 'posted'", record.id)
