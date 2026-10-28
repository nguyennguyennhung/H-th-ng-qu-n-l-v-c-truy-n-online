from django.db import models

from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên thể loại")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Thể loại"
        verbose_name_plural = "Thể loại"
        ordering = ['name']

    def __str__(self):
        return self.name


class Story(models.Model):
    STATUS_CHOICES = (
        ('ongoing', 'Đang ra'),
        ('completed', 'Hoàn thành'),
    )

    title = models.CharField(max_length=255, unique=True, verbose_name="Tên truyện")
    author = models.CharField(max_length=255, default="Đang cập nhật", verbose_name="Tác giả")
    summary = models.TextField(blank=True, verbose_name="Tóm tắt")
    cover_image = models.CharField(max_length=500, blank=True, null=True, verbose_name="URL ảnh bìa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing', verbose_name="Trạng thái")
    categories = models.ManyToManyField(Category, related_name='stories', blank=True, verbose_name="Thể loại")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Truyện"
        verbose_name_plural = "Truyện"
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class Chapter(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters', verbose_name="Truyện")
    chapter_number = models.IntegerField(verbose_name="Số chương")
    title = models.CharField(max_length=255, verbose_name="Tiêu đề chương")
    content = models.TextField(verbose_name="Nội dung chương")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")

    class Meta:
        verbose_name = "Chương"
        verbose_name_plural = "Chương"
        unique_together = ('story', 'chapter_number')
        ordering = ['chapter_number']

    def __str__(self):
        return f"{self.story.title} - Chương {self.chapter_number}: {self.title}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites', verbose_name="Người dùng")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="Truyện")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày lưu")

    class Meta:
        verbose_name = "Yêu thích"
        verbose_name_plural = "Danh sách yêu thích"
        unique_together = ('user', 'story')

    def __str__(self):
        return f"{self.user.username} - {self.story.title}"
