from rest_framework import serializers
from .models import Serie, Author, Chapter
from accounts.models import Review
from django.db.models import Avg, Count

class SerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serie
        fields = "__all__"

class AuthorSerializer(serializers.ModelSerializer):
    series = SerieSerializer(many=True, read_only=True)
    class Meta:
        model = Author
        fields = "__all__"
    def get_series(self, obj):
        series = Serie.objects.filter(authors=obj)
        return SerieSerializer(series, many=True).data

class ChapterSerializer(serializers.ModelSerializer):
    manga = SerieSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    count_rating = serializers.SerializerMethodField()
    class Meta:
        model = Chapter
        fields = "__all__"

    def get_average_rating(self, obj):
        return (
            Review.objects.filter(chapter=obj)
            .aggregate(avg=Avg("rating"))
        )["avg"]

    def get_count_rating(self, obj):
        return (
            Review.objects.filter(chapter=obj)
            .aggregate(count=Count("rating"))
        )["count"]

class SingleSerieSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    class Meta:
        model = Serie
        fields = "__all__"