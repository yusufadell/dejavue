from django.db import models


class Timeline(models.Model):
    """represents a collection of historical events in a specific order."""

    name = models.CharField(max_length=255)
    description = models.TextField()

    events = models.ManyToManyField(
        "events.HistoricalEvent",
        blank=True,
    )

    def __str__(self):
        return self.name


class WhatIfScenario(models.Model):
    """
    allows users to create alternative scenarios
    based on modifying events in a timeline.
    """

    name = models.CharField(max_length=255)
    description = models.TextField()

    original_timeline = models.ForeignKey(
        "timeline.Timeline",
        on_delete=models.CASCADE,
    )
    modified_events = models.ManyToManyField(
        "events.HistoricalEvent",
        related_name="scenarios",
        blank=True,
    )

    class Meta:
        permissions = [
            ("can_create_scenario", "Can create scenario"),
            ("can_edit_scenario", "Can edit scenario"),
            ("can_delete_scenario", "Can delete scenario"),
        ]

    def __str__(self):
        return self.name
