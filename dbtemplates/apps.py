from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DBTemplatesConfig(AppConfig):
    """Config for db templates."""

    name = "dbtemplates"
    verbose_name = _("Database templates")
