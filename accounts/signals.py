from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .documents import ReviewDocument, ProfileDocument
from .models import Review, Profile

from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Review)
def update_review_index(sender, instance, **kwargs):
    """Update Review in Elasticsearch when saved."""
    ReviewDocument().update(instance)

@receiver(post_delete, sender=Review)
def delete_review_index(sender, instance, **kwargs):
    """Delete Review from Elasticsearch when deleted."""
    ReviewDocument().delete(instance)

@receiver(post_save, sender=Profile)
def update_profile_index(sender, instance, **kwargs):
    """Update Profile in Elasticsearch when saved."""
    ProfileDocument().update(instance)

@receiver(post_delete, sender=Profile)
def delete_profile_index(sender, instance, **kwargs):
    """Delete Profile from Elasticsearch when deleted."""
    ProfileDocument().delete(instance)