from odoo import api, fields, models, SUPERUSER_ID
from . import models
from .models import post_init_hook_model
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Post initialization hook to check installed modules."""

    installed_modules = post_init_hook_model(env)
    # Log the installed modules

# Register the post-init hook
# In __init__.py
