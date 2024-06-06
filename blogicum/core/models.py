from django.db import models

from blogicum.constants import MAX_LENGTH_CHAR


class PublishedModel(models.Model):
    """Абстрактная модель.

    Добвляет атрибуты:
    - is_published: поле статуса публикации.
    - created_at: поле с автоматической установкой даты и времени
    создания записи.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        ordering = ('created_at')
        abstract = True


class PublishedTitle(models.Model):
    """Абстрактная модель.

    Добавляет атрибут:
    - title - поле с указанием заголовка.
    """

    title = models.CharField(
        max_length=MAX_LENGTH_CHAR,
        verbose_name='Заголовок'
    )

    class Meta:
        abstract = True
