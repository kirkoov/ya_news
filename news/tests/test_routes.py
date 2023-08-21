from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Стандартным методом Django ORM create() создаём объект класса.
        # Присваиваем объект атрибуту класса: назовём его news.
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    def test_home_page(self):
        # Вместо прямого указания адреса
        # получаем его при помощи функции reverse().
        url = reverse('news:home')
        response = self.client.get(url)
        # Проверяем, что код ответа равен статусу OK (он же 200).
        self.assertEqual(response.status_code, HTTPStatus.OK)
