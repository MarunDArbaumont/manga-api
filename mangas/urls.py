from django.urls import path
from .views import SerieList, AuthorList, ChapterList

urlpatterns = [
    path('series/', SerieList.as_view(), name='series-list'),
    path('authors/', AuthorList.as_view(), name='authors-list'),
    path('chapters/', ChapterList.as_view(), name='chapters-list'),
]