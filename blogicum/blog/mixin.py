"""Модуль с миксинами для модуля blog/views.py."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy

from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from blog.forms import PostForm, CommentForm
from blog.models import Comment, Post


class PostMixin(LoginRequiredMixin):
    """Миксин для создания/отображения/редактирования/удаления публикации.

    Атрибуты класса:
    - model: Класс модели, для создания поста.
    - form_class: Класс формы, для создания поста.
    - template_name: Имя шаблона, для отображения страницы.
    - pk_url_kwarg: Имя переменной, для извлечения объекта.
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        """Возвращает URL перенаправления."""
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentMixin(LoginRequiredMixin):
    """Миксин для редактирования/удаления комментария.

    Атрибуты класса:
    - model: Класс модели, для создания поста.
    - form_class: Класс формы, для создания поста.
    - template_name: Имя шаблона, для отображения страницы.
    - pk_url_kwarg: Имя переменной, для извлечения объекта.
    """

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        """Возвращает коммунтарий."""
        return get_object_or_404(
            Comment,
            id=self.kwargs[self.pk_url_kwarg]
        )

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором комментария."""
        if self.get_object().author != request.user:
            return HttpResponseForbidden(
                "Вы не являетесь автором данного комментария."
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Возвращает URL перенаправления после изменения/удаления поста."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )