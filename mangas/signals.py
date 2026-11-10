"""
Signals for automatic Elasticsearch indexing.
"""
from django.db.models.signals import post_save, post_delete
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
    try:
        SerieDocument().delete(instance.pk)
    except Exception:
        pass  # Silently fail if Elasticsearch is not available

@receiver(post_save, sender=Author)
def update_author_index(sender, instance, **kwargs):
    """Update Author in Elasticsearch when saved."""
    AuthorDocument().update(instance)

@receiver(post_delete, sender=Author)
def delete_author_index(sender, instance, **kwargs):
    """Delete Author from Elasticsearch when deleted."""
    try:
        AuthorDocument().delete(instance.pk)
    except Exception:
        pass  # Silently fail if Elasticsearch is not available

@receiver(post_save, sender=Chapter)
def update_chapter_index(sender, instance, **kwargs):
    """Update Chapter in Elasticsearch when saved."""
    ChapterDocument().update(instance)

@receiver(post_delete, sender=Chapter)
def delete_chapter_index(sender, instance, **kwargs):
    """Delete Chapter from Elasticsearch when deleted."""
    try:
        ChapterDocument().delete(instance.pk)
    except Exception:
        pass  # Silently fail if Elasticsearch is not available
