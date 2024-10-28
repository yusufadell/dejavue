from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.utils.text import slugify

from taggit.managers import TaggableManager


def validate_date_order(start_date, end_date):
    if start_date > end_date:
        msg = "Start date must be before end date."
        raise ValidationError(msg)


class HistoricalEvent(models.Model):
    """represents a specific historical event with its
    details, category, tags, and related events."""

    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
    )  # For events that span multiple dates
    description = models.TextField()
    impact_level = models.IntegerField(
        choices=[(1, "Low"), (2, "Medium"), (3, "High")],
    )
    location = models.ForeignKey(
        "events.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_events = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
    )

    title = models.CharField(max_length=200)
    date = models.DateField()

    significance_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    sources = models.TextField(blank=True)  # References and citations
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    era = models.ForeignKey("events.Era", on_delete=models.CASCADE)
    category = models.ForeignKey(
        "events.EventCategory",
        on_delete=models.CASCADE,
    )
    categories = models.ManyToManyField("events.Category")
    key_figures = models.ManyToManyField(
        "events.HistoricalFigure",
        blank=True,
    )

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def clean(self):
        validate_date_order(self.start_date, self.end_date)


class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_event = models.ForeignKey(
        "events.HistoricalEvent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title


class Scenario(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    events = models.ManyToManyField("events.HistoricalEvent", through="ScenarioEvent")

    def __str__(self):
        return self.title


class ScenarioEvent(models.Model):
    altered_start_date = models.DateField(null=True, blank=True)
    altered_end_date = models.DateField(null=True, blank=True)
    outcome = models.TextField()
    impact = models.IntegerField(
        choices=[
            (1, "Minor"),
            (2, "Significant"),
            (3, "Major"),
        ],
    )

    scenario = models.ForeignKey("events.Scenario", on_delete=models.CASCADE)
    event = models.ForeignKey("events.HistoricalEvent", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.scenario} - {self.event}"


class Prediction(models.Model):
    confidence_level = models.FloatField()
    description = models.TextField()
    name = models.CharField(max_length=255)
    prediction_date = models.DateField()
    prediction_text = models.TextField()

    predicted_event = models.ForeignKey(
        "events.HistoricalEvent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    based_on_events = models.ManyToManyField(
        "events.HistoricalEvent",
        related_name="predictions_based_on",
        blank=True,
    )
    predicted_events = models.ManyToManyField(
        "events.HistoricalEvent",
        related_name="predicted_events",
        blank=True,
    )
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"Prediction {self.name} for {self.scenario}"


class Era(models.Model):
    """Represents major historical eras (e.g., Middle Ages, Renaissance)"""

    name = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    description = models.TextField()
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.start_year} - {self.end_year})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Location(models.Model):
    """Geographical locations for events"""

    name = models.CharField(max_length=200)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    modern_name = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Categories for historical events (e.g., Military, Cultural, Economic)"""

    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class HistoricalFigure(models.Model):
    """Important historical personalities"""

    name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    biography = models.TextField()
    image = models.ImageField(
        upload_to="historical_figures/",
        null=True,
        blank=True,
    )
    bio = models.TextField()

    birthplace = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    associated_events = models.ManyToManyField(
        "events.HistoricalEvent",
        blank=True,
    )

    def __str__(self):
        return self.name


class Consequence(models.Model):
    """Direct and indirect consequences of historical events"""

    event = models.ForeignKey(
        "events.HistoricalEvent",
        on_delete=models.CASCADE,
        related_name="consequences",
    )
    description = models.TextField()
    impact_level = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
    )
    timeframe = models.CharField(max_length=100)  # immediate, short-term, long-term

    def __str__(self):
        return f"Consequence of {self.event}"


class AlternativeScenario(models.Model):
    """What-if scenarios for historical events"""

    original_event = models.ForeignKey(
        "events.HistoricalEvent",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    probability = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
    )
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"What if: {self.title}"


class Timeline(models.Model):
    """Custom timelines created by users"""

    title = models.CharField(max_length=200)
    description = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE)
    events = models.ManyToManyField(
        "events.HistoricalEvent",
        through="TimelineEvent",
        related_name="timelines",
    )

    def __str__(self):
        return self.title


class TimelineEvent(models.Model):
    """Through model for Timeline-Event relationship with additional context"""

    custom_note = models.TextField(blank=True)
    order = models.IntegerField()

    timeline = models.ForeignKey("events.Timeline", on_delete=models.CASCADE)
    event = models.ForeignKey("events.HistoricalEvent", on_delete=models.CASCADE)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.timeline} - {self.event}"


class Resource(models.Model):
    """Additional learning resources"""

    RESOURCE_TYPES = [
        ("DOCUMENT", "Document"),
        ("IMAGE", "Image"),
        ("VIDEO", "Video"),
        ("AUDIO", "Audio"),
        ("LINK", "External Link"),
    ]

    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    content = models.FileField(upload_to="resources/", null=True, blank=True)
    url = models.URLField(blank=True)
    description = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)

    related_event = models.ForeignKey(
        "events.HistoricalEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_by = models.ForeignKey("users.User", on_delete=models.CASCADE)
    events = models.ManyToManyField(
        "events.HistoricalEvent",
        related_name="resources",
    )

    def __str__(self):
        return self.title


class GeopoliticalImpact(models.Model):
    """Track how events affect different regions"""

    impact_type = models.CharField(max_length=50)
    impact_radius = models.FloatField()  # in kilometers
    affected_population = models.IntegerField()
    geometry = models.GeometryField()  # requires GeoDjango

    event = models.ForeignKey("events.HistoricalEvent", on_delete=models.CASCADE)
    region = models.ForeignKey("events.Location", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.event} - {self.region}"


class HistoricalEntity(models.Model):
    """Entities in historical analysis"""

    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(
        upload_to="entities/",
        null=True,
        blank=True,
    )

    location = models.ForeignKey("events.Location", on_delete=models.CASCADE)
    categories = models.ManyToManyField("events.Category")

    tags = TaggableManager()

    def __str__(self):
        return self.name


class HistoricalConnection(models.Model):
    """Relationships between historical entities"""

    relationship_type = models.CharField(max_length=50)
    strength = models.FloatField()
    evidence = models.TextField()

    target = models.ForeignKey(
        "events.HistoricalEntity",
        related_name="incoming_connections",
        on_delete=models.CASCADE,
    )
    source = models.ForeignKey(
        "events.HistoricalEntity",
        related_name="outgoing_connections",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.source} -> {self.target}"


class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class EventTag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Cause(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Effect(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class CauseEffectRelationship(models.Model):
    description = models.TextField()

    cause = models.ForeignKey(
        "events.Cause",
        on_delete=models.CASCADE,
    )
    effect = models.ForeignKey(
        "events.Effect",
        on_delete=models.CASCADE,
    )
    historical_event = models.ForeignKey(
        "events.HistoricalEvent",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.cause} -> {self.effect} in {self.historical_event}"
