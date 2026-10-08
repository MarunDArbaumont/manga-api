from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from .models import Profile, Review, ReviewReaction
from mangas.serializers import ChapterSerializer

class UserSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "picture"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"write_only": True, "required": True},
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            return serializers.ValidationError("This email is already used.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def get_picture(self, obj):
        profile = getattr(obj, "profile", None)
        if profile and profile.profile_picture:
            return profile.profile_picture.url
        return None

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'mangas', 'bio', 'profile_picture', 'user']
        read_only_fields = ["mangas"]
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
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = "__all__"

    def get_likes(self, obj):
        if hasattr(obj, "likes_count"):
            return obj.likes_count
        return obj.reactions.filter(reaction=ReviewReaction.LIKE).count()

    def get_dislikes(self, obj):
        if hasattr(obj, "dislikes_count"):
            return obj.dislikes_count
        return obj.reactions.filter(reaction=ReviewReaction.DISLIKE).count()

    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        mine = getattr(obj, "my_reactions", None)
        if mine is None:
            r = obj.reactions.filter(user=request.user).first()
            return r.reaction if r else None
        return mine[0].reaction if mine else None

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