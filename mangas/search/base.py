from elasticsearch import Elasticsearch, exceptions as es_exceptions
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
import logging

logger = logging.getLogger(__name__)

class SearchView(APIView):
    """
    Base view for Elasticsearch-powered search endpoints.

    Subclasses should define:
    - index_name: The Elasticsearch index to search
    - document_class: The Django-ES document class
    - serializer_class: DRF serializer for results
    - fallback_queryset: Django queryset for fallback
    """

    index_name = None
    document_class = None
    serializer_class = None
    fallback_queryset = None

    # Default page size
    page_size = 20

    def get_elasticsearch_client(self):
        """Get configured Elasticsearch client."""
        return Elasticsearch(
            hosts=[settings.ELASTICSEARCH_URL],
            timeout=settings.ELASTICSEARCH_TIMEOUT,
            # Add auth if configured
            basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
            if hasattr(settings, 'ELASTICSEARCH_USER') else None
        )

    def build_elasticsearch_query(self, query_params):
        """
        Build ES query from request parameters.
        Override in subclasses for custom query logic.
        """
        raise NotImplementedError("Subclasses must implement build_elasticsearch_query")

    def execute_elasticsearch_query(self, es_client, query):
        """Execute query against Elasticsearch."""
        try:
            return es_client.search(
                index=self.index_name,
                body=query,
                size=self.page_size
            )
        except es_exceptions.ConnectionError as e:
            logger.error(f"Elasticsearch connection error: {e}")
            return None
        except es_exceptions.TransportError as e:
            logger.error(f"Elasticsearch transport error: {e}")
            return None
        except Exception as e:
            logger.error(f"Elasticsearch query error: {e}")
            return None

    def execute_fallback_query(self, query_params):
        """
        Execute fallback database query.
        Override in subclasses for custom fallback logic.
        """
        queryset = self.fallback_queryset
        # Apply basic filtering if query exists
        search_query = query_params.get('q', '')
        if search_query:
            # Simple fallback: filter by title/name containing query
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        return queryset[:self.page_size]

    def get(self, request, *args, **kwargs):
        """Main GET handler for search requests."""
        query_params = request.query_params.dict()

        # Try Elasticsearch first
        es_client = self.get_elasticsearch_client()
        es_query = self.build_elasticsearch_query(query_params)

        # Check if ES is available
        if self._is_elasticsearch_available(es_client):
            es_results = self.execute_elasticsearch_query(es_client, es_query)

            if es_results is not None:
                return self.format_elasticsearch_response(es_results)

        # Fallback to database
        logger.warning("Falling back to database query for search")
        fallback_results = self.execute_fallback_query(query_params)
        serializer = self.serializer_class(fallback_results, many=True)
        return Response({
            'results': serializer.data,
            'meta': {
                'source': 'database',
                'count': len(serializer.data)
            }
        })

    def _is_elasticsearch_available(self, es_client):
        """Check if Elasticsearch is reachable."""
        try:
            return es_client.ping()
        except Exception:
            return False

    def format_elasticsearch_response(self, es_results):
        """Format ES results into consistent response structure."""
        hits = es_results.get('hits', {}).get('hits', [])

        # Extract document IDs
        doc_ids = [int(hit['_id']) for hit in hits]

        # Get full documents from database (to ensure we have all fields)
        if self.fallback_queryset:
            documents = self.fallback_queryset.filter(pk__in=doc_ids)
            serializer = self.serializer_class(documents, many=True)

            # Create a mapping from id to serialized data
            serialized_map = {str(doc['id']): doc for doc in serializer.data}

            # Reorder to match ES relevance
            ordered_results = []
            for hit in hits:
                doc_id = hit['_id']
                if doc_id in serialized_map:
                    result = serialized_map[doc_id]
                    result['_score'] = hit['_score']
                    ordered_results.append(result)

            return Response({
                'results': ordered_results,
                'meta': {
                    'source': 'elasticsearch',
                    'total': es_results['hits']['total']['value'],
                    'page_size': self.page_size
                }
            })

        return Response({
            'results': [],
            'meta': {
                'source': 'elasticsearch',
                'error': 'No fallback queryset configured'
            }
        })