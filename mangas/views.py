from django.db import models
from django.db.models import Avg, Count, Prefetch
from rest_framework import generics, filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
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
from .search.base import SearchView
from .documents import SerieDocument, AuthorDocument, ChapterDocument

class SerieView(generics.ListCreateAPIView):
    serializer_class = SerieSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SerieFilter
    ordering_fields = ["title", "first_published", "average_rating"]
    ordering = ["title"]

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
                Prefetch("authors"),
            )
            .order_by("title")
        )

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
    queryset = Author.objects.prefetch_related("mangas__authors").order_by("name")
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
    queryset = chapters_with_ratings().order_by("manga", "number")
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ChapterFilter
    ordering_fields =["first_published", "manga", "average_rating"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ChapterWriteSerializer
        return ChapterSerializer

class SeriesSearchView(SearchView):
    index_name = 'series'
    document_class = SerieDocument
    serializer_class = SerieSerializer
    fallback_queryset = Serie.objects.all()

    def build_elasticsearch_query(self, query_params):
        query = {
            'query': {
                'bool': {
                    'must': []
                }
            }
        }

        search_term = query_params.get('q', '')
        if search_term:
            query['query']['bool']['should'] = [
                {
                    'match': {
                        'title': {
                            'query': search_term,
                            'fuzziness': 'AUTO'
                        }
                    }
                },
                {
                    'match': {
                        'authors': {
                            'query': search_term,
                            'fuzziness': 'AUTO'
                        }
                    }
                }
            ]

        # Add filters
        genre = query_params.get('genre')
        if genre:
            query['query']['bool']['must'].append({
                'term': {'genre': genre}
            })

        # Add sorting
        sort_by = query_params.get('sort', 'relevance')
        if sort_by == 'rating':
            query['sort'] = [{'average_rating': {'order': 'desc'}}]
        elif sort_by == 'date':
            query['sort'] = [{'first_published': {'order': 'desc'}}]

        return query

class AuthorsSearchView(SearchView):
    index_name = 'authors'
    document_class = AuthorDocument
    serializer_class = AuthorSerializer
    fallback_queryset = Author.objects.all()

    def build_elasticsearch_query(self, query_params):
        query = {
            'query': {
                'bool': {
                    'must': []
                }
            }
        }

        search_term = query_params.get('q', '')
        if search_term:
            query['query']['bool']['should'] = [
                {
                    'match': {
                        'name': {
                            'query': search_term,
                            'fuzziness': 'AUTO'
                        }
                    }
                },
                {
                    'match': {
                        'manga_titles': {
                            'query': search_term,
                            'fuzziness': 'AUTO'
                        }
                    }
                }
            ]

        sort_by = query_params.get('sort', 'relevance')
        if sort_by == 'date':
            query['sort'] = [{'birth_day': {'order': 'desc'}}]

        return query

class ChaptersSearchView(SearchView):
    index_name = 'chapters'
    document_class = ChapterDocument
    serializer_class = ChapterSerializer
    fallback_queryset = Chapter.objects.all()

    def build_elasticsearch_query(self, query_params):
        query = {
            'query': {
                'bool': {
                    'must': []
                }
            }
        }

        search_term = query_params.get('q', '')
        if search_term:
            query['query']['bool']['should'] = [
                {
                    'match': {
                        'name': {
                            'query': search_term,
                            'fuzziness': 'AUTO'
                        }
                    }
                },
                {
                    'match': {
                        'manga_title': {
                            'query': search_term,
                            'fuzziness': 'AUTO'
                        }
                    }
                }
            ]
            try:
                float(search_term)
                query['query']['bool']['should'].append({
                    'term': {
                        'number': float(search_term)
                    }
                })
            except ValueError:
                pass

            query['query']['bool']['minimum_should_match'] = 1

        sort_by = query_params.get('sort', 'relevance')
        if sort_by == 'date':
            query['sort'] = [{'first_published': {'order': 'desc'}}]

        return query