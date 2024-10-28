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


class HistoricalPattern(models.Model):
    """AI-detected patterns across historical events"""

    name = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField()
    supporting_events = models.ManyToManyField("events.HistoricalEvent")
    pattern_type = models.CharField(
        max_length=50,
        choices=[
            ("CYCLICAL", "Cyclical Pattern"),
            ("CAUSAL", "Cause-Effect Pattern"),
            ("BEHAVIORAL", "Human Behavior Pattern"),
        ],
    )

    def __str__(self):
        return self.name


class PredictiveModel(models.Model):
    """ML model predictions for future events"""

    title = models.CharField(max_length=200)
    prediction = models.TextField()
    probability = models.FloatField()
    based_on_patterns = models.ManyToManyField(HistoricalPattern)
    relevant_factors = JSONField()
    prediction_date = models.DateTimeField()

    def __str__(self):
        return self.title
