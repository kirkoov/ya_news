import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from http import HTTPStatus

from django.urls import reverse


# Главная страница доступна анонимному пользователю.
# + Страницы регистрации пользователей, входа в учётную запись и выхода из неё
# доступны анонимным пользователям.
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Страница отдельной новости доступна анонимному пользователю.
@pytest.mark.parametrize(
    'name',
    ('news:detail',)
)
@pytest.mark.django_db
def test_news_page_availability_for_anonymous_user(
    client, name, news, news_id_for_args
):
    url = reverse(name, args=news_id_for_args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Страницы удаления и редактирования комментария доступны автору комментария.
# + Авторизованный пользователь не может зайти на страницы редактирования или
# удаления чужих комментариев (возвращается ошибка 404).
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# При попытке перейти на страницу редактирования или удаления комментария
# анонимный пользователь перенаправляется на страницу авторизации.
@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:edit', lazy_fixture('comment')),
        ('news:delete', lazy_fixture('comment')),
    ),
)
@pytest.mark.django_db
def test_redirects(client, name, comment_object):
    login_url = reverse('users:login')
    # Формируем URL в зависимости от того, передан ли объект заметки:
    url = reverse(name, args=(comment_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
