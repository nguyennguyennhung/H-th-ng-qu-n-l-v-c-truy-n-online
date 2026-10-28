from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User

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

# ==================== 4. NHÓM VIEW GIAO DIỆN WEB ====================


def home_view(request):
    stories = Story.objects.all().prefetch_related('categories', 'chapters')
    
    # Xử lý tìm kiếm theo tên
    search_query = request.GET.get('search')
    if search_query:
        stories = stories.filter(title__icontains=search_query)

    # Xử lý lọc theo thể loại
    category_id = request.GET.get('category')
    if category_id:
        stories = stories.filter(categories__id=category_id)

    categories = Category.objects.all()

    context = {
        'stories': stories,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'stories/home.html', context)
def story_detail_view(request, pk):
    story = get_object_or_404(Story.objects.prefetch_related('categories', 'chapters'), pk=pk)
    chapters = story.chapters.all().order_by('chapter_number')
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, story=story).exists()
    context = {
        'story': story,
        'chapters': chapters,
    }
    return render(request, 'stories/story_detail.html', context)

def chapter_detail_view(request, pk):
    chapter = get_object_or_404(Chapter.objects.select_related('story'), pk=pk)
    story = chapter.story
    
    # Tìm chương trước và chương sau
    prev_chapter = Chapter.objects.filter(story=story, chapter_number__lt=chapter.chapter_number).order_by('-chapter_number').first()
    next_chapter = Chapter.objects.filter(story=story, chapter_number__gt=chapter.chapter_number).order_by('chapter_number').first()
    
    # Danh sách tất cả các chương để phục vụ menu chọn nhanh
    all_chapters = story.chapters.all().order_by('chapter_number')

    context = {
        'chapter': chapter,
        'story': story,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'all_chapters': all_chapters,
    }
    return render(request, 'stories/chapter_detail.html', context)
# Bấm Thêm/Bỏ yêu thích trên web
def toggle_favorite_web(request, pk):
    if not request.user.is_authenticated:
        return redirect('/dang-nhap/?next=/truyen/' + str(pk) + '/')
    story = get_object_or_404(Story, pk=pk)
    fav = Favorite.objects.filter(user=request.user, story=story).first()
    if fav:
        fav.delete()
    else:
        Favorite.objects.create(user=request.user, story=story)
    return redirect('web-story-detail', pk=pk)

# Trang xem danh sách yêu thích
def favorite_list_view(request):
    if not request.user.is_authenticated:
        return redirect('/dang-nhap/?next=/yeu-thich/')
    favorites = Favorite.objects.filter(user=request.user).select_related('story')
    return render(request, 'stories/favorites.html', {'favorites': favorites})

# Trang đăng nhập trên web
def login_web_view(request):
    error = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            error = "Tên đăng nhập hoặc mật khẩu không chính xác!"
    return render(request, 'stories/login.html', {'error': error})

# Đăng xuất trên web
def logout_web_view(request):
    logout(request)
    return redirect('/')
from django.contrib.auth.models import User

def register_web_view(request):
    error = None
    success = None
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        cp = request.POST.get('confirm_password')

        if p != cp:
            error = "Mật khẩu xác nhận không khớp!"
        elif User.objects.filter(username=u).exists():
            error = "Tên đăng nhập đã tồn tại!"
        else:
            # Cố tình không kiểm tra độ dài 8 ký tự và chữ số -> Chấp nhận luôn mật khẩu 'abc'
            User.objects.create_user(username=u, email=e, password=p)
            success = "Đăng ký thành công!"
    return render(request, 'stories/register.html', {'error': error, 'success': success})


