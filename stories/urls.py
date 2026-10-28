from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    CategoryListAPIView,
    StoryListAPIView,
    StoryDetailAPIView,
    StoryChaptersAPIView,
    ChapterDetailAPIView,
    FavoriteListAPIView,
    ToggleFavoriteAPIView,
    home_view,
    story_detail_view,
    chapter_detail_view,
    toggle_favorite_web,
    favorite_list_view,
    login_web_view,
    logout_web_view,
    register_web_view,

)

urlpatterns = [
    path('', home_view, name='web-home'),
    path('truyen/<int:pk>/', story_detail_view, name='web-story-detail'),
    path('chuong/<int:pk>/', chapter_detail_view, name='web-chapter-detail'),
    path('truyen/<int:pk>/yeu-thich/', toggle_favorite_web, name='web-toggle-favorite'),
    path('yeu-thich/', favorite_list_view, name='web-favorites'),
    path('dang-nhap/', login_web_view, name='web-login'),
    path('dang-xuat/', logout_web_view, name='web-logout'),
    path('register/', register_web_view, name='web-register'),
    path('api/auth/register/', RegisterAPIView.as_view(), name='api-auth-register'),




    # 1. Auth API
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('auth/me/', ProfileAPIView.as_view(), name='api-profile'),

    # 2. Truyện & Thể loại API
    path('categories/', CategoryListAPIView.as_view(), name='api-categories'),
    path('stories/', StoryListAPIView.as_view(), name='api-stories'),
    path('stories/<int:pk>/', StoryDetailAPIView.as_view(), name='api-story-detail'),
    path('stories/<int:story_id>/chapters/', StoryChaptersAPIView.as_view(), name='api-story-chapters'),
    path('chapters/<int:pk>/', ChapterDetailAPIView.as_view(), name='api-chapter-detail'),

    # 3. Yêu thích API
    path('favorites/', FavoriteListAPIView.as_view(), name='api-favorites'),
    path('stories/<int:pk>/favorite/', ToggleFavoriteAPIView.as_view(), name='api-toggle-favorite'),
]
