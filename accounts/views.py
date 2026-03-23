from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import ProfileSerializer, UserSerializer
from .models import Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        user_id = request.user.id
        return Response({"id": user_id, "username": username})

class ProfileView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer