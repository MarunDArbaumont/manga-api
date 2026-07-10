from django.urls import path, include
from .views import SerieView, AuthorView, ChapterViewSet, SerieByIdView, AuthorByIdView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("chapters", ChapterViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("series/", SerieView.as_view(), name='series-list'),
    path("series/<int:pk>/", SerieByIdView.as_view()),
    path("authors/", AuthorView.as_view(), name='authors-list'),
    path("authors/<int:pk>/", AuthorByIdView.as_view()),
]