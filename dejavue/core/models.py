from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models import JSONField


class QualityMetrics(models.Model):
    """Track and ensure content quality"""

    object_id = models.PositiveIntegerField()
    accuracy_score = models.FloatField()
    completeness_score = models.FloatField()
    source_reliability = models.FloatField()
    peer_review_status = models.CharField(max_length=20)

    content_object = GenericForeignKey("content_type", "object_id")
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.content_object} - {self.accuracy_score}"


class HistoricalPattern(models.Model):
    """AI-detected patterns across historical events"""

    name = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField()
    pattern_type = models.CharField(
        max_length=50,
        choices=[
            ("CYCLICAL", "Cyclical Pattern"),
            ("CAUSAL", "Cause-Effect Pattern"),
            ("BEHAVIORAL", "Human Behavior Pattern"),
        ],
    )

    supporting_events = models.ManyToManyField("events.HistoricalEvent")

    def __str__(self):
        return self.name


class PredictiveModel(models.Model):
    """ML model predictions for future events"""

    title = models.CharField(max_length=200)
    prediction = models.TextField()
    probability = models.FloatField()
    relevant_factors = JSONField()
    prediction_date = models.DateTimeField()

    based_on_patterns = models.ManyToManyField("core.HistoricalPattern")

    def __str__(self):
        return self.title


class FactCheck(models.Model):
    """Verification of historical claims"""

    claim = models.TextField()
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ("VERIFIED", "Verified"),
            ("DISPUTED", "Disputed"),
            ("DEBUNKED", "Debunked"),
        ],
    )
    evidence = models.TextField()
    confidence_score = models.FloatField()

    verified_by = models.ManyToManyField(
        "users.User",
        limit_choices_to={"is_staff": True},
    )

    def __str__(self):
        return self.claim
