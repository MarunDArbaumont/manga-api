from rest_framework import serializers
from .models import Serie, Author, Chapter

class SerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serie
        fields = ['id', 'title', 'first_published', 'last_published', 'description']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name', 'birth_day', 'death_date']

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['number', 'name', 'first_published', 'manga_id']
