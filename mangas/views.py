from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Serie, Author, Chapter
from .serializers import SerieSerializer, ChapterSerializer, AuthorSerializer

class SerieView(APIView):
    def get(self, request):
        ALLOWED_FILTER = (
            "genre",
            "title"
        )
        request_params = request.query_params
        if len(request_params) == 0:
            queryset = Serie.objects.all().order_by("title")
            serializer = SerieSerializer(queryset, many=True)
            return Response(serializer.data)
        filters = {}
        for k, v in request_params.items():
            if k not in ALLOWED_FILTER:
                raise ValidationError("please enter a valid filter")
            filters[k] = v
                
        print(f"This is the filter we want in the filter method: {filters}")
        queryset = Serie.objects.filter(**filters).order_by("title")
        serializer = SerieSerializer(queryset, many=True)
        return Response(serializer.data)
        

class AuthorView(APIView):
    def get(self, request):
        queryset = Author.objects.all().order_by("name")
        serializer = AuthorSerializer(queryset, many=True)
        return Response(serializer.data)

class ChapterView(APIView):
    def get(self, request):
        queryset = Chapter.objects.all().order_by("manga_id")
        serializer = ChapterSerializer(queryset, many=True)
        return Response(serializer.data)
