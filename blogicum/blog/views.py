from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect

from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from blogicum.constants import NUM_OF_POSTS
from .models import User, Post, Category, Comment
from .forms import ProfileForm, PostForm, CommentForm
from .mixin import PostMixin, CommentMixin
from .utils import get_all_post_published_query

from django.db.models import Count


class IndexListView(ListView):
    """Главная страница со списком публикаций.

    Атрибуты класса:
        - model: Класс модели, для получения данных.
        - template_name: Имя шаблона, для отображения страницы.
        - queryset: Запрос, определяющий список постов для отображения.
        - paginate_by: Количество публикаций на одной странице.
    """

    model = Post
    template_name = 'blog/index.html'
    queryset = get_all_post_published_query()
    paginate_by = NUM_OF_POSTS


class ProfileView(ListView):
    """Страница со списком публикаций пользователя.

    Атрибуты класса:
    - template_name: Имя шаблона, для отображения страницы.
    - author: Автор публикации.
    - pk_url_kwarg: Имя переменной, для извлечения объекта.
    - paginate_by: Количество публикаций на одной странице.
    """

    model = Post
    template_name = 'blog/profile.html'
    pk_url_kwarg = 'username'
    paginate_by = NUM_OF_POSTS

    def get_queryset(self):
        """Возвращает список публикаций автора."""
        profile = get_object_or_404(
            User,
            username=self.kwargs[self.pk_url_kwarg]
        )
        if self.request.user == profile:
            return (
                Post.objects
                .filter(author=profile)
                .annotate(comment_count=Count('comments'))
                .order_by('-pub_date')
            )
        else:
            return get_all_post_published_query().filter(author=profile)

    def get_context_data(self, **kwargs):
        """Возвращает контекстные данные для шаблона."""
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            User,
            username=self.kwargs[self.pk_url_kwarg]
        )
        context['profile'] = profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля пользователя.

    Атрибуты класса:
    - model: Класс модели, для получения данных.
    - form_class: Класс формы, для обновления профиля пользователя.
    - template_name: Имя шаблона, для отображения страницы.
    """

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Возвращает объект пользователя для обновления."""
        return self.request.user

    def get_success_url(self):
        """Возвращает URL для перенаправления после обновления профиля."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class PostDetailView(PostMixin, DetailView):
    """Страница выбранного поста.

    Атрибуты класса:
    - template_name: Имя шаблона, для отображения страницы.
    """

    template_name = 'blog/detail.html'

    def get_object(self):
        """Возвращает пост."""
        post = get_object_or_404(
            Post,
            pk=self.kwargs[self.pk_url_kwarg]
        )
        if self.request.user == post.author:
            return post
        else:
            return get_object_or_404(
                Post.post_objects.all(),
                pk=self.kwargs[self.pk_url_kwarg]
            )

    def get_context_data(self, **kwargs):
        """Возвращает контекстные данные для шаблона."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.get_object()
            .comments.all()
            .order_by('created_at')
            )
        return context


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    """Создание поста."""

    def form_valid(self, form):
        """Проверяет, форму и устанавливает автора поста."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Возвращает URL для перенаправления после создания поста."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    """Редактирование поста."""

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором поста."""
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    """Удаление поста."""

    def dispatch(self, request, *args, **kwargs):
        """Проверяет, является ли пользователь автором поста."""
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Возвращает контекстные данные для шаблона."""
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        """Возвращает URL перенаправления после удаления поста."""
        username = self.request.user
        return reverse_lazy('blog:profile',
                            kwargs={'username': username})


class CategoryDetailView(IndexListView):
    """Страница со списком постов выбранной категории.

    Атрибуты класса:
    - template_name: Имя шаблона, используемого для отображения страницы.
    """

    template_name = 'blog/category.html'

    def get_queryset(self):
        """Возвращает список публикаций в категории."""
        slug = self.kwargs['category_slug']
        self.category = get_object_or_404(
            Category, slug=slug, is_published=True
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        """Возвращает контекстные данные для шаблона."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария.

    Атрибуты класса:
    - model: Класс модели, используемой для создания комментария.
    - form_class: Класс формы, используемый для создания комментария.
    - template_name: Имя шаблона, используемого для отображения страницы.
    - post_data: Объект поста, к которому создается комментарий.
    """

    model = Comment
    form_class = CommentForm
    template_name = 'include/comments.html'
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        """Получает объект поста."""
        self.post_data = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Проверяет форму и устанавливает автора комментария."""
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        if self.post_data.author != self.request.user:
            self.send_author_email()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Возвращает контекстные данные для шаблона."""
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return context

    def send_author_email(self):
        """Отправляет email автору поста, при добавлении комментария."""
        post_url = self.request.build_absolute_uri(self.get_success_url())
        recipient_email = self.post_data.author.email
        subject = 'New comment'
        message = (
            f'Пользователь {self.request.user} оставил комментарий '
            f'к посту {self.post_data.title}.'
            f'Читать комментарий {post_url}'
        )
        send_mail(
            subject=subject,
            message=message,
            from_email="from@example.com",
            recipient_list=[recipient_email],
            fail_silently=True,
        )

    def get_success_url(self):
        """Возвращает URL перенаправления."""
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(CommentMixin, LoginRequiredMixin, UpdateView):
    """Редактирование комментария.

    CommentMixin: Базовый класс, предоставляющий функциональность.
    """


class CommentDeleteView(CommentMixin, LoginRequiredMixin, DeleteView):
    """Удаление комментария.

    CommentMixin: Базовый класс, предоставляющий функциональность.
    """