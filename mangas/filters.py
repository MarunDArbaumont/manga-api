import django_filters
from .models import Serie, Author, Chapter

class SerieFilter(django_filters.FilterSet):
    ongoing = django_filters.BooleanFilter(field_name="last_published", method="is_empty")

    def is_empty(self, queryset, name, value):
        lookup = "__".join([name, "isnull"])
        return queryset.filter(**{lookup: value})

    class Meta:
        model = Serie
        fields = ["genre", "title", "ongoing"]

class AuthorFilter(django_filters.FilterSet):
    class Meta:
        model = Author
        fields = ["name"]

class ChapterFilter(django_filters.FilterSet):
    class Meta:
        model = Chapter
        fields = ["manga", "number"]
