from django.urls import path
from .views import UserView, ProfileView, UserByIdView, CurrentUserView, ProfileByIdView, ReviewView

urlpatterns = [
    path("users", UserView.as_view(), name='users-list'),
    path("profiles", ProfileView.as_view(), name='profile-list'),
    path("users/<int:pk>/", UserByIdView.as_view()),
    path("profiles/<int:user>/", ProfileByIdView.as_view()),
    path("reviews", ReviewView.as_view()),
    path("me", CurrentUserView.as_view(), name='current-user'),
]