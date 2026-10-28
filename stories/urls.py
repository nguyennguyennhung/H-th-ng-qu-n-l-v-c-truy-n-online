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
    ToggleFavoriteAPIView
)

urlpatterns = [
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
