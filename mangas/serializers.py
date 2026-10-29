from rest_framework import serializers
from .models import Serie, Author, Chapter
from accounts.models import Review
from django.db.models import Avg, Count

class SerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serie
        fields = "__all__"
        extra_kwargs = {
            "cover": {"use_url": False}
        }

class AuthorSerializer(serializers.ModelSerializer):
    series = SerieSerializer(many=True, read_only=True, source="mangas")

    class Meta:
        model = Author
        fields = "__all__"
        extra_kwargs = {
            "image": {"use_url": False}
        }

class ChapterSerializer(serializers.ModelSerializer):
    manga = SerieSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    count_rating = serializers.SerializerMethodField()
    number = serializers.DecimalField(max_digits=6, decimal_places=1, coerce_to_string=False)
    class Meta:
        model = Chapter
        fields = "__all__"

    def get_average_rating(self, obj):
        if hasattr(obj, "average_rating"):
            return obj.average_rating
        return (
            Review.objects.filter(chapter=obj)
            .aggregate(avg=Avg("rating"))
        )["avg"]

    def get_count_rating(self, obj):
        if hasattr(obj, "count_rating"):
            return obj.count_rating
        return (
            Review.objects.filter(chapter=obj)
            .aggregate(count=Count("rating"))
        )["count"]

class ChapterWriteSerializer(serializers.ModelSerializer):
    number = serializers.DecimalField(max_digits=6, decimal_places=1, coerce_to_string=False)
    class Meta:
        model = Chapter
        fields = ["id", "number", "name", "manga", "first_published"]


class SingleSerieSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    count_rating = serializers.SerializerMethodField()

    class Meta:
        model = Serie
        fields = "__all__"
        extra_kwargs = {
            "cover": {"use_url": False}
        }

    def get_average_rating(self, obj):
        if hasattr(obj, "average_rating"):
            return obj.average_rating
        return (
            Review.objects.filter(chapter__manga=obj)
            .aggregate(avg=Avg("rating"))
        )["avg"]

    def get_count_rating(self, obj):
        if hasattr(obj, "count_rating"):
            return obj.count_rating
        return (
            Review.objects.filter(chapter__manga=obj)
            .aggregate(count=Count("rating"))
        )["count"]
