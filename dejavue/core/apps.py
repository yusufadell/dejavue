from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dejavue.core"

    def ready(self):
        from core.permissions import create_permissions

        post_migrate.connect(create_permissions, sender=self)
