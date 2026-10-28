from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from .models import Category, Story, Chapter, Favorite
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CategorySerializer, 
    StoryListSerializer, 
    StoryDetailSerializer, 
    ChapterDetailSerializer,
    ChapterSimpleSerializer,
    FavoriteSerializer
)

# ==================== 1. NHÓM API AUTHENTICATION ====================

# Đăng ký: POST /api/auth/register/
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Đăng ký thành công!",
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Đăng nhập: POST /api/auth/login/
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Đăng nhập thành công!",
                "token": token.key,
                "user": UserSerializer(user).data
            })
        return Response({"error": "Sai tên đăng nhập hoặc mật khẩu."}, status=status.HTTP_400_BAD_REQUEST)


# Đăng xuất: POST /api/auth/logout/
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Xóa token để kết thúc phiên đăng nhập
        Token.objects.filter(user=request.user).delete()
        return Response({"message": "Đăng xuất thành công!"})


# Thông tin user hiện tại: GET /api/auth/me/
class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ==================== 2. NHÓM API TRUYỆN & CHƯƠNG ====================

# Danh sách thể loại: GET /api/categories/
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Danh sách truyện: GET /api/stories/?search=...&category=...&status=...
class StoryListAPIView(generics.ListAPIView):
    serializer_class = StoryListSerializer

    def get_queryset(self):
        queryset = Story.objects.all().prefetch_related('categories', 'chapters')
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


# Chi tiết 1 truyện: GET /api/stories/<id>/
class StoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Story.objects.all().prefetch_related('categories', 'chapters')
    serializer_class = StoryDetailSerializer


# Danh sách tất cả chương của 1 truyện: GET /api/stories/<story_id>/chapters/
class StoryChaptersAPIView(APIView):
    def get(self, request, story_id):
        story = get_object_or_404(Story, pk=story_id)
        chapters = story.chapters.all()
        serializer = ChapterSimpleSerializer(chapters, many=True)
        return Response(serializer.data)


# Đọc 1 chương cụ thể: GET /api/chapters/<id>/
class ChapterDetailAPIView(generics.RetrieveAPIView):
    queryset = Chapter.objects.all().select_related('story')
    serializer_class = ChapterDetailSerializer


# ==================== 3. NHÓM API YÊU THÍCH ====================

# Xem danh sách yêu thích của tôi: GET /api/favorites/
class FavoriteListAPIView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('story')


# Thêm/Bỏ yêu thích (Toggle): POST /api/stories/<id>/favorite/
class ToggleFavoriteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        story = get_object_or_404(Story, pk=pk)
        fav = Favorite.objects.filter(user=request.user, story=story).first()
        if fav:
            fav.delete()
            return Response({"message": f"Đã bỏ yêu thích truyện '{story.title}'.", "is_favorited": False})
        else:
            Favorite.objects.create(user=request.user, story=story)
            return Response({"message": f"Đã thêm truyện '{story.title}' vào yêu thích.", "is_favorited": True}, status=status.HTTP_201_CREATED)
