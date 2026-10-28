import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from stories.models import Category, Story, Chapter, Favorite

User = get_user_model()

class Command(BaseCommand):
    help = "Script nạp dữ liệu mẫu cho hệ thống đọc truyện"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Đang dọn dẹp dữ liệu cũ..."))
        # 1. Xóa dữ liệu cũ (để mỗi lần chạy lại không bị trùng)
        Chapter.objects.all().delete()
        Favorite.objects.all().delete()
        Story.objects.all().delete()
        Category.objects.all().delete()

        # 2. Tạo thể loại mẫu
        self.stdout.write("Đang tạo thể loại...")
        categories_data = ["Trinh thám", "Đam mỹ", "Ngôn Tình", "Đô Thị", "Hiện đại"]
        cat_objs = []
        for cat_name in categories_data:
            cat = Category.objects.create(name=cat_name, description=f"Thể loại {cat_name}")
            cat_objs.append(cat)

        # 3. Tạo tài khoản độc giả mẫu để tester đăng nhập thử
        self.stdout.write("Đang tạo tài khoản độc giả...")
        reader, created = User.objects.get_or_create(username="reader1", defaults={"email": "reader1@example.com"})
        if created:
            reader.set_password("Matkhau123@")  # Băm mật khẩu chuẩn của Django
            reader.save()

        # 4. Danh sách 5 truyện mẫu
        sample_stories = [
            {"title": "Mưa", "author": "T", "summary": "một hai ba..."},
            {"title": "Nắng", "author": "U", "summary": "một hai ba..."},
            {"title": "Bão", "author": "K", "summary": "một hai ba..."},
            {"title": "Gios", "author": "C", "summary": "một hai ba..."},
            {"title": "Sương", "author": "H", "summary": "một hai ba..."},
        ]

        # 5. Vòng lặp tạo truyện & chương
        self.stdout.write("Đang tạo truyện và chương...")
        created_stories = []
        for item in sample_stories:
            # Ngẫu nhiên trạng thái: 'ongoing' (Đang ra) hoặc 'completed' (Hoàn thành)
            random_status = random.choice(['ongoing', 'completed'])

            story = Story.objects.create(
                title=item["title"],
                author=item["author"],
                summary=item["summary"],
                cover_image="https://picsum.photos/300/400",  # Link ảnh bìa mẫu
                status=random_status
            )

            # Gán ngẫu nhiên 1 - 2 thể loại cho truyện
            assigned_cats = random.sample(cat_objs, k=random.randint(1, 2))
            story.categories.set(assigned_cats)
            created_stories.append(story)

            # Tạo ngẫu nhiên từ 1 đến 5 chương cho mỗi truyện
            num_chapters = random.randint(1, 5)
            for ch_num in range(1, num_chapters + 1):
                Chapter.objects.create(
                    story=story,
                    chapter_number=ch_num,
                    title=f"Chương {ch_num}: Một",
                    content=f"Đây là nội dung chương {ch_num} của truyện {story.title}. Dữ liệu mẫu phục vụ kiểm thử hệ thống đọc truyện."
                )

        # 6. Tạo 1 - 2 yêu thích mẫu cho tài khoản reader1
        if created_stories:
            Favorite.objects.create(user=reader, story=created_stories[0])

        self.stdout.write(self.style.SUCCESS("==> Nạp dữ liệu mẫu thành công!"))
