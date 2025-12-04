from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Serie, Author, Chapter
from .serializers import SerieSerializer, ChapterSerializer, AuthorSerializer

class SerieList(APIView):
    def get(self, request):
        queryset = Serie.objects.all().order_by("title")
        serializer = SerieSerializer(queryset, many=True)
        return Response(serializer.data)

class AuthorList(APIView):
    def get(self, request):
        queryset = Author.objects.all().order_by("name")
        serializer = AuthorSerializer(queryset, many=True)
        return Response(serializer.data)

class ChapterList(APIView):
    def get(self, request):
        queryset = Chapter.objects.all().order_by("manga_id")
        serializer = ChapterSerializer(queryset, many=True)
        return Response(serializer.data)
