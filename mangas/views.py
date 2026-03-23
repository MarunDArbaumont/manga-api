from rest_framework import generics, filters
from django.contrib.auth.models import User
from .models import Serie, Author, Chapter
from .serializers import SerieSerializer, ChapterSerializer, AuthorSerializer, SingleSerieSerializer
from .filters import SerieFilter, AuthorFilter, ChapterFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

class SerieView(generics.ListCreateAPIView):
    queryset = Serie.objects.all()
    serializer_class = SerieSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SerieFilter
    ordering_fields = ["title", "first_published"]
    ordering = ["title"]

class SerieByIdView(generics.RetrieveAPIView):
    queryset = Serie.objects.prefetch_related("chapters")
    serializer_class = SingleSerieSerializer


class AuthorView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AuthorFilter
    ordering_fields = ["name", "birth_day"]
    ordering = ["name"]

class AuthorByIdView(generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class ChapterView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ChapterFilter
    ordering_fields =["first_published", "manga"]

class ChapterByIdView(generics.RetrieveAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
