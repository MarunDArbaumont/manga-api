from django.db.models import Avg, Count, Prefetch
from rest_framework import generics, filters, viewsets

from .filters import AuthorFilter, ChapterFilter, SerieFilter
from .models import Author, Chapter, Serie
from .permissions import IsAdminOrReadOnly
from .querysets import chapters_with_ratings
from .serializers import (
    AuthorSerializer,
    ChapterSerializer,
    ChapterWriteSerializer,
    SerieSerializer,
    SingleSerieSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend

class SerieView(generics.ListCreateAPIView):
    queryset = Serie.objects.prefetch_related("authors")
    serializer_class = SerieSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SerieFilter
    ordering_fields = ["title", "first_published"]
    ordering = ["title"]

class SerieByIdView(generics.RetrieveAPIView):
    serializer_class = SingleSerieSerializer

    def get_queryset(self):
        chapters = chapters_with_ratings().order_by("number")
        return (
            Serie.objects
            .annotate(
                average_rating=Avg("chapters__review__rating"),
                count_rating=Count("chapters__review__rating"),
            )
            .prefetch_related(
                Prefetch("chapters", queryset=chapters),
                "authors__mangas__authors",
            )
        )


class AuthorView(generics.ListCreateAPIView):
    queryset = Author.objects.prefetch_related("mangas__authors")
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AuthorFilter
    ordering_fields = ["name", "birth_day"]
    ordering = ["name"]

class AuthorByIdView(generics.RetrieveAPIView):
    queryset = Author.objects.prefetch_related("mangas__authors")
    serializer_class = AuthorSerializer

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = chapters_with_ratings()
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ChapterFilter
    ordering_fields =["first_published", "manga"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ChapterWriteSerializer
        return ChapterSerializer
