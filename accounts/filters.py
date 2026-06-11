import django_filters
from .models import Profile, Review

class ProfileFilter(django_filters.FilterSet):
    class Meta:
        model = Profile
        fields = ["user"]


class ReviewFilter(django_filters.FilterSet):
    class Meta:
        model = Review
        fields = ["user", "chapter"]