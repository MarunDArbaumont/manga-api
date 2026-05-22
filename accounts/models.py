from django.db import models
from mangas.models import Chapter
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    bio = models.CharField(max_length=255)
    mangas = models.ManyToManyField(Chapter, "collection")

    def __str__(self):
        return f"This profile belongs to {self.user}"