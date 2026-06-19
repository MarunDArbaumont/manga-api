from django.contrib.auth.models import User
from rest_framework import generics, filters, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import ProfileSerializer, UserSerializer, SingleUserSerializer, SingleProfileSerializer, ReviewSerializer, ReviewCreateSerializer, ReviewEditSerializer
from .models import Profile, Review
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProfileFilter, ReviewFilter
from mangas.models import Chapter
from django.shortcuts import get_object_or_404

class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserByIdView(generics.RetrieveAPIView):
    queryset = User.objects
    serializer_class = SingleUserSerializer

class ProfileByIdView(generics.RetrieveAPIView):
    queryset = Profile.objects.prefetch_related("mangas")
    serializer_class = SingleProfileSerializer
    def get_object(self):
        user_id = self.kwargs["user_id"]
        return get_object_or_404(Profile, user_id=user_id)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        user_id = request.user.id
        return Response({"id": user_id, "username": username})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        if self.action in ["update", "partial_update"]:
            return ReviewEditSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_edited=True)

    def get_queryset(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return Review.objects.filter(user=self.request.user)
        return Review.objects.all()


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def add_manga(self, request, pk=None):
        profile = request.user.profile

        manga_id = request.data.get("chapter")
        if not manga_id:
            return Response({"error": "chapter required"}, status=400)

        manga = get_object_or_404(Chapter, pk=manga_id)
        profile.mangas.add(manga)
        return Response({"message": f"Added {manga.name} to collection"})

    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def remove_manga(self, request, pk=None):
        profile = request.user.profile

        manga_id = request.data.get("chapter")
        if not manga_id:
            return Response({"error": "chapter required"}, status=400)

        manga = get_object_or_404(Chapter, pk=manga_id)
        profile.mangas.remove(manga)
        return Response({"message": f"Removed {manga.name} to collection"})
    