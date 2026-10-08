from django.urls import path, include
from .views import UserView, UserByIdView, ProfileByIdView, ReviewViewSet, ProfileViewSet, CsrfView, LoginView, LogoutView, MeView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("reviews", ReviewViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("users/", UserView.as_view(), name='users-list'),
    path("users/<int:pk>/", UserByIdView.as_view()),
    path("users/<int:user_id>/profile/", ProfileByIdView.as_view()),
    path("auth/csrf/", CsrfView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("me/", MeView.as_view(), name='current-user'),
]