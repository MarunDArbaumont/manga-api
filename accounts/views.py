from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Prefetch, Q
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, filters, viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import ProfileSerializer, UserSerializer, SingleUserSerializer, SingleProfileSerializer, ReviewSerializer, ReviewCreateSerializer, ReviewEditSerializer
from .models import Profile, Review, ReviewReaction
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProfileFilter, ReviewFilter
from .permissions import IsOwnerOrReadOnly, SignupThrottle
from .throttles import LoginThrottle
from mangas.models import Chapter
from mangas.querysets import chapters_with_ratings
from django.shortcuts import get_object_or_404

import logging

logger = logging.getLogger("accounts")

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """Pose le cookie csrftoken. À appeler une fois au chargement de l'app."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        user = authenticate(
            request,
            username=request.data.get("username"),
            password=request.data.get("password"),
        )
        if user is None:
            return Response(
                {"detail": "Identifiants invalides"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        login(request, user)  # crée la session + pose le cookie sessionid
        return Response({"id": user.id, "username": user.username})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "username": u.username})

class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    throttle_classes = [SignupThrottle]
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]

class UserByIdView(generics.RetrieveAPIView):
    queryset = User.objects
    serializer_class = SingleUserSerializer

class ProfileByIdView(generics.RetrieveAPIView):
    queryset = Profile.objects.prefetch_related(
        Prefetch("mangas", queryset=chapters_with_ratings())
    )
    serializer_class = SingleProfileSerializer
    def get_object(self):
        user_id = self.kwargs["user_id"]
        return get_object_or_404(Profile, user_id=user_id)

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
        logger.debug(f"{self.request.user} has created a new review")

    def perform_update(self, serializer):
        serializer.save(is_edited=True)

    def get_queryset(self):
        user = self.request.user

        qs = Review.objects.select_related(
            "user__profile", "chapter__manga"
        ).prefetch_related("chapter__manga__authors").annotate(
            likes_count=Count("reactions", filter=Q(reactions__reaction=ReviewReaction.LIKE)),
            dislikes_count=Count("reactions", filter=Q(reactions__reaction=ReviewReaction.DISLIKE)),
        )

        if user.is_authenticated:
            qs = qs.prefetch_related(
                Prefetch(
                    "reactions",
                    queryset=ReviewReaction.objects.filter(user=user),
                    to_attr="my_reactions",
                )
            )
            if self.action in ["update", "partial_update", "destroy"]:
                qs = qs.filter(user=user)
        elif self.action in ["update", "partial_update", "destroy"]:
            return Review.objects.none()

        return qs
    
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        review = self.get_object()
        reaction, _ = ReviewReaction.objects.update_or_create(
            user=request.user,
            review=review,
            defaults={"reaction": ReviewReaction.LIKE},
        )
        return Response({"message": "Liked"})
    
    @action(detail=True, methods=["delete"])
    def reaction(self, request, pk=None):
        review = self.get_object()
        ReviewReaction.objects.filter(
            user=request.user,
            review=review,
        ).delete()
        return Response({"message": "Reaction removed"})
    
    @action(detail=True, methods=["post"])
    def dislike(self, request, pk=None):
        review = self.get_object()
        reaction, _ = ReviewReaction.objects.update_or_create(
            user=request.user,
            review=review,
            defaults={"reaction": ReviewReaction.DISLIKE},
        )
        return Response({"message": "Disliked"})


class ProfileViewSet(mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
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
    