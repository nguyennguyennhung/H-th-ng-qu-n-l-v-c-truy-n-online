from django.contrib import admin
from .models import Category, Story, Chapter, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ('chapter_number', 'title')

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'status', 'updated_at')
    list_filter = ('status', 'categories')
    search_fields = ('title', 'author')
    inlines = [ChapterInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'story', 'chapter_number', 'title', 'created_at')
    list_filter = ('story',)
    search_fields = ('title', 'story__title')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'story', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'story__title')
