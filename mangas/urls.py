from django.urls import path
from .views import SerieView, AuthorView, ChapterView

urlpatterns = [
    path('series', SerieView.as_view(), name='series-list'),
    path('authors', AuthorView.as_view(), name='authors-list'),
    path('chapters', ChapterView.as_view(), name='chapters-list'),
]