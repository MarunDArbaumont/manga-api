from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Review, ReviewReaction
from mangas.serializers import ChapterSerializer

class UserSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "picture"]
        extra_kwargs = {
            "password": {"write_only": True},
            "picture": {"use_url": False}
            }

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user

    def get_picture(self, obj):
        if hasattr(obj, "profile") and obj.profile.profile_picture:
            return obj.profile.profile_picture.url
        return None

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'mangas', 'bio', 'profile_picture', 'user']
        extra_kwargs = {
            "profile_picture": {"use_url": False}
        }

class SingleProfileSerializer(serializers.ModelSerializer):
    mangas = ChapterSerializer(many=True, read_only=True)
    class Meta:
        model = Profile
        fields = "__all__"
        extra_kwargs = {
            "profile_picture": {"use_url": False}
        }

class SingleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

class ReviewSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = "__all__"

    def get_likes(self, obj):
        return obj.reactions.filter(
            reaction=ReviewReaction.LIKE
        ).count()

    def get_dislikes(self, obj):
        return obj.reactions.filter(
            reaction=ReviewReaction.DISLIKE
        ).count()

class ReviewReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReaction
        fields = "__all__"

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "description", "chapter", "parent"]
    
    def validate(self, attrs):
        parent = attrs.get("parent")
        rating = attrs.get("rating")

        if parent is None and rating is None:
            raise serializers.ValidationError("Reviews require a rating")

        if parent is not None and rating is not None:
            raise serializers.ValidationError("Comments cannot have a rating")
        
        return attrs

class ReviewEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "description"]

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields =["profile_picture"]
        extra_kwargs = {
            "profile_picture": {"use_url": False}
        }