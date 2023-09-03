from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


# Анонимный пользователь не может отправить комментарий.
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


# Авторизованный пользователь может отправить комментарий.
def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(
        response, reverse('news:detail', args=(news.id,)) + '#comments'
    )
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


# Если комментарий содержит запрещённые слова, он не будет опубликован, а форма
# вернёт ошибку.
def test_user_cant_use_bad_words(admin_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


# Авторизованный пользователь может редактировать или удалять свои комментарии.
def test_author_can_edit_comment(author_client, form_data, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(
        response, reverse('news:detail', args=(news.id,)) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, comment, news):
    response = author_client.delete(reverse('news:delete', args=(comment.id,)))
    assertRedirects(
        response, reverse('news:detail', args=(news.id,)) + '#comments'
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


# Авторизованный пользователь не может редактировать или удалять чужие
# комментарии.
def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, form_data
):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
