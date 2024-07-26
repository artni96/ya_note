from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from notes.models import Note
from django.contrib.auth import get_user_model
from copy import copy


User = get_user_model()


class TestRoutes(TestCase):
    def url_creator(self, name, slug):
        return reverse(
            f'notes:{name}', args=slug)

    @classmethod
    def setUpTestData(cls) -> None:

        cls.HOME_PAGE_URL = reverse('notes:home')
        cls.author = User.objects.create(username='author')
        cls.test_user = User.objects.create(username='test_user')
        cls.test_note = Note.objects.create(
            title='тестовая заметка',
            text='текст тестовой заметки',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_user)
        cls.url_list_for_author = [
            ('edit', (cls.test_note.slug,)),
            ('delete', (cls.test_note.slug,)),
        ]
        cls.url_list_for_user = [
            ('detail', (cls.test_note.slug,)),
            ('success', None),
            ('add', None)
        ]

    def test_anonymous_access_pages(self):
        """Проверка доступности страниц для неавторизованных пользователей."""
        url_list = (
            self.HOME_PAGE_URL,
            reverse('users:login'),
            reverse('users:logout'),
            reverse('users:signup')
        )
        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_user(self):
        """Проверка доступности страниц для авторизованных пользователей."""
        url_list = copy(self.url_list_for_user)
        url_list = [self.url_creator(url[0], url[1]) for url in url_list]
        for url in url_list:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_only_author_can_work_with_notes(self):
        """Проверяется случай, когда только автор
        может работать со своими заметками."""
        url_list = copy(self.url_list_for_author)
        url_list = [self.url_creator(url[0], url[1]) for url in url_list]
        user_status_choice = (
            (self.author_client, HTTPStatus.OK),
            (self.authorized_client, HTTPStatus.NOT_FOUND)
        )
        for user, status in user_status_choice:
            for url in url_list:
                with self.subTest(url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Тестирование редиректов в случае, если посетитель неавторизован."""
        url_list = copy(self.url_list_for_author)
        url_list = [self.url_creator(url[0], url[1]) for url in url_list]
        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f'{reverse("users:login")}?next={url}'
                self.assertRedirects(response, redirect_url)
