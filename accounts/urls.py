from django.urls import path
from .views import UserView, ProfileView, UserByIdView

urlpatterns = [
    path('users', UserView.as_view(), name='users-list'),
    path('profiles', ProfileView.as_view(), name='profile-list'),
    path("users/<int:pk>/", UserByIdView.as_view()),
]