from django.contrib.auth.models import User
from rest_framework import generics, filters
from rest_framework.views import APIView
from .serializers import ProfileSerializer, UserSerializer, SingleUserSerializer
from .models import Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProfileFilter

class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

class UserByIdView(generics.RetrieveAPIView):
    queryset = User.objects
    serializer_class = SingleUserSerializer

class ProfileView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter]
    filterset_class = ProfileFilter
    serializer_class = ProfileSerializer

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        user_id = request.user.id
        return Response({"id": user_id, "username": username})