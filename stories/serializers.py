from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Story, Chapter, Favorite

User = get_user_model()

# ==================== AUTH SERIALIZERS ====================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được sử dụng.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Mật khẩu xác nhận không khớp."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # Băm mật khẩu tự động
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


# ==================== STORY & CHAPTER SERIALIZERS ====================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ChapterSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'chapter_number', 'title', 'created_at']


class ChapterDetailSerializer(serializers.ModelSerializer):
    story_title = serializers.CharField(source='story.title', read_only=True)
    prev_chapter_id = serializers.SerializerMethodField()
    next_chapter_id = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'story', 'story_title', 'chapter_number', 'title', 'content', 'prev_chapter_id', 'next_chapter_id', 'created_at']

    def get_prev_chapter_id(self, obj):
        prev_ch = Chapter.objects.filter(story=obj.story, chapter_number__lt=obj.chapter_number).order_by('-chapter_number').first()
        return prev_ch.id if prev_ch else None

    def get_next_chapter_id(self, obj):
        next_ch = Chapter.objects.filter(story=obj.story, chapter_number__gt=obj.chapter_number).order_by('chapter_number').first()
        return next_ch.id if next_ch else None


class StoryListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    total_chapters = serializers.IntegerField(source='chapters.count', read_only=True)

    class Meta:
        model = Story
        fields = ['id', 'title', 'author', 'summary', 'cover_image', 'status', 'categories', 'total_chapters', 'updated_at']


class StoryDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    chapters = ChapterSimpleSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'title', 'author', 'summary', 'cover_image', 'status', 'categories', 'chapters', 'is_favorited', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, story=obj).exists()
        return False


# ==================== FAVORITE SERIALIZER ====================
class FavoriteSerializer(serializers.ModelSerializer):
    story = StoryListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'story', 'created_at']
