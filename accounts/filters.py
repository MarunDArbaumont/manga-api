import django_filters
from .models import Profile, Review

class ReviewFilter(django_filters.FilterSet):
    class Meta:
        model = Review
        fields = ["user", "chapter", "parent"]