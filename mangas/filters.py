import django_filters
from django.db.models import Avg, Count, Q
from .models import Serie, Author, Chapter

class SerieFilter(django_filters.FilterSet):
    ongoing = django_filters.BooleanFilter(field_name="last_published", method="is_empty")
    average_rating_min = django_filters.NumberFilter(field_name="average_rating", method="filter_by_min_rating")
    average_rating_max = django_filters.NumberFilter(field_name="average_rating", method="filter_by_max_rating")

    def is_empty(self, queryset, name, value):
        lookup = "__".join([name, "isnull"])
        return queryset.filter(**{lookup: value})
    
    def filter_by_min_rating(self, queryset, name, value):
        if "average_rating" not in queryset.query.annotations:
            queryset = queryset.annotate(average_rating=Avg("chapters__review__rating"))
        return queryset.filter(average_rating__gte=value)

    def filter_by_max_rating(self, queryset, name, value):
        return queryset.filter(average_rating__lte=value)

    class Meta:
        model = Serie
        fields = ["genre", "title", "ongoing", "average_rating_min", "average_rating_max"]

class AuthorFilter(django_filters.FilterSet):
    class Meta:
        model = Author
        fields = ["name"]

class ChapterFilter(django_filters.FilterSet):
    class Meta:
        model = Chapter
        fields = ["manga", "number"]
