from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestHomePage(TestCase):
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        all_news = []
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
            news = News(title=f'Новость {index}', text='Просто текст.')
            all_news.append(news)
        News.objects.bulk_create(all_news)

    def test_news_count(self):
        response = self.client.get(TestHomePage.HOME_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Проверяем, что на странице именно нужное число новостей.
        self.assertEqual(
            len(response.context['news_list']),
            settings.NEWS_COUNT_ON_HOME_PAGE
        )
