from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class QualityMetrics(models.Model):
    """Track and ensure content quality"""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    accuracy_score = models.FloatField()
    completeness_score = models.FloatField()
    source_reliability = models.FloatField()
    peer_review_status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.content_object} - {self.accuracy_score}"
