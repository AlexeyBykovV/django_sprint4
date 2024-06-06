"""Модуль с вызовом ошибок.

Шаблоны для этих страниц находятся в директории templates/pages/.
"""
from django.shortcuts import render


def csrf_failure(request, reason=''):
    """Вернуть ошибку 403csrf."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception=None):
    """Вернуть ошибку 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request, exception=None):
    """Вернуть ошибку 500."""
    return render(request, "pages/500.html", status=500)
