from django.db import models
from django.db.models import JSONField


class Interaction(models.Model):
    interaction_type = models.CharField(
        max_length=50,
        choices=[
            ("view", "Viewed"),
            ("edit", "Edited"),
            ("create", "Created"),
            ("predict", "Predicted"),
        ],
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        "events.HistoricalEvent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    scenario = models.ForeignKey(
        "events.Scenario",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} \
            on {self.event or self.scenario}"


class Simulation(models.Model):
    """Interactive historical simulations"""

    title = models.CharField(max_length=200)
    scenario = models.ForeignKey(
        "events.AlternativeScenario",
        on_delete=models.CASCADE,
    )
    parameters = JSONField()
    difficulty_level = models.IntegerField(
        choices=[
            (1, "Easy"),
            (2, "Medium"),
            (3, "Hard"),
        ],
    )

    def __str__(self):
        return self.title


class UserDecision(models.Model):
    """Track user decisions in simulations"""

    decision_point = models.CharField(max_length=200)
    choice_made = models.TextField()
    outcome = models.TextField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.simulation} - {self.decision_point}"


class HistoricalDebate(models.Model):
    """Platform for scholarly debates"""

    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=[
            ("ACTIVE", "Active"),
            ("CONCLUDED", "Concluded"),
            ("ARCHIVED", "Archived"),
        ],
    )

    topic = models.ForeignKey("events.HistoricalEvent", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Argument(models.Model):
    """Arguments in historical debates"""

    content = models.TextField()
    sources = models.TextField()
    credibility_score = models.FloatField()

    debate = models.ForeignKey("interactions.HistoricalDebate", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.debate}"
