from django.urls import path
from .views import UserView, CurrentUserView, ProfileView

urlpatterns = [
    path('users', UserView.as_view(), name='users-list'),
    path('me', CurrentUserView.as_view(), name='current-user'),
    path('profiles', ProfileView.as_view(), name='profile-list'),
]