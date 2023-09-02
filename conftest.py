import pytest

from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_id_for_args(news):
    # И возвращает кортеж, который содержит id новости.
    return news.id,


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment
