from odoo import api, SUPERUSER_ID
from . import settings_configurations
from . import invoices
from . import api_config
from . import res_model
from . import crm_leads
from . import custom_model
import logging

_logger = logging.getLogger(__name__)

# Define the flag
SALE_MODULE_INSTALLED = False

def post_init_hook_model(cr, registry):
    """Post initialization hook to check installed modules."""
    global SALE_MODULE_INSTALLED
    env = api.Environment(cr, SUPERUSER_ID, {})
    installed_modules = env['custom.model'].get_installed_modules()
    # Log the installed modules
    _logger.info(f"Installed modules from models/init file: {installed_modules}")
    if 'sale' in installed_modules:
        # Set the flag to True if the 'sale' module is installed
        SALE_MODULE_INSTALLED = True
        _logger.info("The 'sale' module is installed. Setting the flag to True.")
    else:
        _logger.info("The 'sale' module is not installed")

# Register the post init hook in the manifest
try:
    post_init_hook_model()
except Exception as e:
    _logger.error(f"Post initialization hook error: {e}")

# Conditionally import sales_orders based on the flag
if SALE_MODULE_INSTALLED:
    try:
        from . import sales_orders
        _logger.info("Successfully imported sales_orders module.")
    except ImportError as e:
        _logger.error(f"Error importing sales_orders: {e}")
else:
    _logger.info("The 'sale' module is not installed. Skipping sales_orders import.")

DEPENDENCIES = ['base']
