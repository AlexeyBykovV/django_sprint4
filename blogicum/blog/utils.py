"""Модуль с утилитами для модуля blog/views."""
from django.db.models import Count

from .models import Post


def get_all_post_published_query():
    """Вернуть все посты."""
    queryset = (
        Post.post_objects
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    return queryset
