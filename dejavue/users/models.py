from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from django.db import models
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Dejavue.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interest_areas = models.ManyToManyField(
        "events.HistoricalEvent",
        blank=True,
    )
    created_scenarios = models.ManyToManyField(
        "events.Scenario",
        related_name="created_by_user",
    )
    viewed_events = models.ManyToManyField(
        "events.HistoricalEvent",
        related_name="viewed_by",
    )

    def __str__(self):
        return self.user.username


class Achievement(models.Model):
    """Achievements that users can earn"""

    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.name


class UserProgress(models.Model):
    """Track user learning progress"""

    knowledge_score = models.FloatField()
    learning_path = JSONField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    topics_mastered = models.ManyToManyField(
        "events.Category",
    )
    achievements = models.ManyToManyField(
        "users.Achievement",
    )

    def __str__(self):
        return self.user
