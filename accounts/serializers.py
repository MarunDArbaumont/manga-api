from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Review
from mangas.serializers import ChapterSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["user", "bio", "mangas", "profile_picture"]

class SingleProfileSerializer(serializers.ModelSerializer):
    mangas = ChapterSerializer(many=True, read_only=True)
    class Meta:
        model = Profile
        fields = "__all__"

class SingleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

class ReviewSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = "__all__"

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "description", "chapter"]

class ReviewEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "description"]
