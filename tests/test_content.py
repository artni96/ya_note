from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.NOTES_PAGE_URL = reverse('notes:list')
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        Note.objects.bulk_create(
            [
                Note(
                    title=f'Заметка {i}',
                    text=f'Текст для заметки {i}',
                    slug=f'slug_{i}',
                    author=cls.author)
                for i in range(1, 4)
            ]
        )

    def test_main_page_content(self):
        """Тестирование контента страницы с заметками."""
        response = self.author_client.get(self.NOTES_PAGE_URL)
        user_notes = self.author.notes.all()
        self.assertEqual(
            response.context['object_list'].count(),
            user_notes.count()
        )
