from django.contrib import admin

from .models import Category, Location, Post, Comment


class BlogAdmin(admin.ModelAdmin):
    """Общий интерфейс админки."""

    list_editable = ("is_published",)


class PostInline(admin.TabularInline):
    """Шаблон, используемый для отображения редактирования."""

    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(BlogAdmin):
    """Админка для Категорий."""

    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'is_published',
    )
    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(BlogAdmin):
    """Админка для Местоположения."""

    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published',
    )
    search_fields = (
        'name',
    )


@admin.register(Post)
class PostAdmin(BlogAdmin):
    """Админка для Публикаций."""

    list_display = (
        'is_published',
        'title',
        'pub_date',
        'text',
        'author',
        'category',
        'location',
        'created_at',
    )
    list_editable = (
        'pub_date',
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для Комментариев."""

    list_display = (
        'text',
        'post',
        'author',
        'created_at',
    )
    list_filter = ('text',)
