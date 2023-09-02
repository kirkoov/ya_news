import pytest
from pytest_lazyfixture import lazy_fixture

from django.conf import settings
from django.urls import reverse


# Количество новостей на главной странице — не более 10.
# +Новости отсортированы от самой свежей к самой старой.
# +Свежие новости в начале списка.
@pytest.mark.django_db
def test_homepage_has_given_num_news(client, create_news):
    response = client.get(reverse('news:home'))
    news_list = response.context['news_list']
    assert len(news_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


# Комментарии на странице отдельной новости отсортированы от старых к новым:
# +старые в начале списка, новые — в конце.
@pytest.mark.django_db
def test_comments_sorted_from_old_to_new(news, admin_client, create_comments):
    detail_url = reverse('news:detail', args=(news.id,))
    response = admin_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


# Анонимному пользователю недоступна форма для отправки комментария на странице
# +отдельной новости, а авторизованному доступна.
@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (lazy_fixture('author_client'), True),
        (lazy_fixture('client'), False),
    )
)
@pytest.mark.django_db
def test_news_comment_form_for_different_users(
        news, parametrized_client, note_in_list
):
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is note_in_list


# Автору комментария доступна форма редактирования своего комментария
def test_news_comment_edit_form_for_author(
        author_client, news, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.get(url)
    assert 'form' in response.context
