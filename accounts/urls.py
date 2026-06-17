from django.urls import path,include
from .views import UserView, UserByIdView, CurrentUserView, ProfileByIdView, ReviewViewSet, ProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("reviews", ReviewViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("users/", UserView.as_view(), name='users-list'),
    path("users/<int:pk>/", UserByIdView.as_view()),
    path("users/<int:user_id>/profile/", ProfileByIdView.as_view()),
    path("me/", CurrentUserView.as_view(), name='current-user'),
]