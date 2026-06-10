from django.db import models
from mangas.models import Chapter
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    bio = models.CharField(blank=True, null=True, max_length=255)
    mangas = models.ManyToManyField(Chapter, "collection")

    def __str__(self):
        return f"This profile belongs to {self.user}"

class Review(models.Model):
    REVIEW_RATING_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    rating = models.IntegerField(blank=True, null=True, choices=REVIEW_RATING_CHOICES)
    description = models.CharField(blank=True, null=True, max_length=255)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)