from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from .models import Profile, Review, ReviewReaction
from mangas.serializers import ChapterSerializer
from mangas.querysets import chapters_with_ratings

class UserSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "picture"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already used.")
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
        read_only_fields = ["mangas", "user"]
        extra_kwargs = {
            "profile_picture": {"use_url": False}
        }

    def validate(self, attrs):
        if 'user' in attrs:
            raise serializers.ValidationError(
                {"user": "You cannot change the user associated with this profile."}
            )
        return attrs

    def validate_profile_picture(self, value):
        if value.content_type not in ["image/png", "image/jpeg", "image/webp"]:
            raise ValidationError("Profile picture must be PNG, JPEG, or WebP format")
        if value.size > 5 * 1024 * 1024:
            raise ValidationError("Profile picture must be less than 5MB")
        return value

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
    chapter = chapters_with_ratings()
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
        chapter = attrs.get("chapter")
        rating = attrs.get("rating")

        if parent is not None and chapter is not None:
            raise serializers.ValidationError("Reviews can't have a parent and a chapter")

        if parent is None and rating is None:
            raise serializers.ValidationError("Reviews require a rating")

        if parent is not None and rating is not None:
            raise serializers.ValidationError("Comments cannot have a rating")

        if parent is None and chapter is None:
            raise serializers.ValidationError("Reviews require a chapter")
        
        return attrs

class ReviewEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "description"]
    
    def validate(self, attrs):
        rating = attrs.get("rating")
        parent = self.instance.parent if self.instance else None

        if rating is not None and parent is not None:
            raise serializers.ValidationError("A reply shouldn't have a rating")

        if parent is None and rating is None and "rating" in attrs:
            raise serializers.ValidationError("Top-level reviews must have a rating")

        return attrs

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields =["profile_picture"]
        extra_kwargs = {
            "profile_picture": {"use_url": False}
        }