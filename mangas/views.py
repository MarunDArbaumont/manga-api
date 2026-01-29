from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Serie, Author, Chapter
from .serializers import SerieSerializer, ChapterSerializer, AuthorSerializer

class SerieView(APIView):
    def get(self, request):
        ALLOWED_DIRECT_FIELD_FILTER = (
            "genre",
            "title"
        )
        ALLOWED_SEMANTIC_FILTER = (
            "ongoing",
            "order_by"
        )
        queryset = Serie.objects.all()
        request_params = request.query_params
        if len(request_params) == 0:
            
            serializer = SerieSerializer(queryset, many=True)
            return Response(serializer.data)
        filters = {}
        for k, v in request_params.items():
            if k in ALLOWED_SEMANTIC_FILTER:
                if k == "ongoing" and v:
                    queryset = queryset.filter(last_published__isnull=True)
                    continue
                if k == "order_by" and v.endswith("_desc"):
                    ordered = "-" + v.replace("_desc", "")
                    queryset = queryset.order_by(ordered)
                    continue
                elif k == "order_by" and v.endswith("_asc"):
                    queryset = queryset.order_by(v.replace("_asc", ""))
                    continue
            if k not in ALLOWED_DIRECT_FIELD_FILTER:
                raise ValidationError(f"please enter a query params from these lists: {ALLOWED_DIRECT_FIELD_FILTER}, {ALLOWED_SEMANTIC_FILTER}")
            filters[k] = v
        queryset = queryset.filter(**filters)
        serializer = SerieSerializer(queryset, many=True)
        return Response(serializer.data)
        

class AuthorView(APIView):
    def get(self, request):
        queryset = Author.objects.all().order_by("name")
        serializer = AuthorSerializer(queryset, many=True)
        return Response(serializer.data)

class ChapterView(APIView):
    def get(self, request):
        ALLOWED_DIRECT_FIELD_FILTER = (
            "manga",
            "number"
        )
        request_params = request.query_params
        if len(request_params) == 0:
            queryset = Chapter.objects.all().order_by("manga_id")
            serializer = ChapterSerializer(queryset, many=True)
            return Response(serializer.data)
        filters = {}
        for k, v in request_params.items():
            if k not in ALLOWED_DIRECT_FIELD_FILTER:
                raise ValidationError("please enter valid filter")
            filters[k] = v
        queryset = Chapter.objects.filter(**filters)
        serializer = ChapterSerializer(queryset, many=True)
        return Response(serializer.data)
