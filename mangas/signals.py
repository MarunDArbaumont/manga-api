"""
Signals for automatic Elasticsearch indexing.
"""
from django.db.models.signals import post_save, post_delete, post_bulk_create, post_bulk_update, post_bulk_delete
from django.dispatch import receiver
from .documents import SerieDocument, AuthorDocument, ChapterDocument
from .models import Serie, Author, Chapter

@receiver(post_save, sender=Serie)
def update_serie_index(sender, instance, **kwargs):
    """Update Serie in Elasticsearch when saved."""
    SerieDocument().update(instance)

@receiver(post_delete, sender=Serie)
def delete_serie_index(sender, instance, **kwargs):
    """Delete Serie from Elasticsearch when deleted."""
    SerieDocument().delete(instance)

@receiver(post_save, sender=Author)
def update_author_index(sender, instance, **kwargs):
    """Update Author in Elasticsearch when saved."""
    AuthorDocument().update(instance)

@receiver(post_delete, sender=Author)
def delete_author_index(sender, instance, **kwargs):
    """Delete Author from Elasticsearch when deleted."""
    AuthorDocument().delete(instance)

@receiver(post_save, sender=Chapter)
def update_chapter_index(sender, instance, **kwargs):
    """Update Chapter in Elasticsearch when saved."""
    ChapterDocument().update(instance)

@receiver(post_delete, sender=Chapter)
def delete_chapter_index(sender, instance, **kwargs):
    """Delete Chapter from Elasticsearch when deleted."""
    ChapterDocument().delete(instance)

@receiver(post_bulk_create, sender=Serie)
def update_bulk_serie_index(sender, instances, **kwargs):
    """Update multiple Series in Elasticsearch after bulk create."""
    SerieDocument().update(instances)

@receiver(post_bulk_update, sender=Serie)
def update_bulk_serie_index(sender, instances, **kwargs):
    """Update multiple Series in Elasticsearch after bulk update."""
    SerieDocument().update(instances)

@receiver(post_bulk_delete, sender=Serie)
def delete_bulk_serie_index(sender, instances, **kwargs):
    """Delete multiple Series from Elasticsearch after bulk delete."""
    SerieDocument().delete(instances)