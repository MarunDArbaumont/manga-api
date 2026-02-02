from rest_framework import generics
from rest_framework import filters
from .models import Serie, Author, Chapter
from .serializers import SerieSerializer, ChapterSerializer, AuthorSerializer
from .filters import SerieFilter, AuthorFilter, ChapterFilter
from django_filters.rest_framework import DjangoFilterBackend

class SerieView(generics.ListAPIView):
    queryset = Serie.objects.all()
    serializer_class = SerieSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SerieFilter
    ordering_fields = ["title", "first_published"]
    ordering = ["title"]


class AuthorView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AuthorFilter
    ordering_fields = ["name", "birth_day"]
    ordering = ["name"]

class ChapterView(generics.ListAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ChapterFilter
    ordering_fields =["first_published", "manga"]
