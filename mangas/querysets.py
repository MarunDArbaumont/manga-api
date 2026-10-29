from django.db.models import Avg, Count

from .models import Chapter


def chapters_with_ratings():
    """Return chapters with their review aggregates annotated."""
    return (
        Chapter.objects
        .select_related("manga")
        .prefetch_related("manga__authors")
        .annotate(
            average_rating=Avg("review__rating"),
            count_rating=Count("review__rating"),
        )
    )
