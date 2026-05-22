from django.urls import path
from .views import SerieView, AuthorView, ChapterView, SerieByIdView, AuthorByIdView, ChapterByIdView

urlpatterns = [
    path('series', SerieView.as_view(), name='series-list'),
    path("series/<int:pk>/", SerieByIdView.as_view()),
    path('authors', AuthorView.as_view(), name='authors-list'),
    path("authors/<int:pk>/", AuthorByIdView.as_view()),
    path('chapters', ChapterView.as_view(), name='chapters-list'),
    path("chapters/<int:pk>/", ChapterByIdView.as_view()),
]