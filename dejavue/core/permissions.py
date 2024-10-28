from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from dejavue.timeline.models import WhatIfScenario


def create_permissions(app_config, verbosity=2, **kwargs):
    content_type = ContentType.objects.get_for_model(WhatIfScenario)
    Permission.objects.get_or_create(
        codename="can_create_scenarios",
        name="Can create What-If scenarios",
        content_type=content_type,
    )
