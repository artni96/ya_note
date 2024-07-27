from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from pprint import pp


User = get_user_model()


class TestCreateContentCase(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Тестовый текст заметки'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.add_note_url = reverse('notes:add')
        cls.form = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT}
        cls.user = User.objects.create(username='test_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    def test_anonym_cant_create_note(self):
        response = self.client.post(
            self.add_note_url,
            data=self.form
        )
        redirect_url = f'{reverse("users:login")}?next={self.add_note_url}'
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        self.auth_client.post(
            self.add_note_url,
            data=self.form
        )
        user_notes = self.user.notes.all()
        self.assertEqual(user_notes.count(), 1)
        self.assertEqual(user_notes.first().text, self.NOTE_TEXT)
        self.assertEqual(user_notes.first().title, self.NOTE_TITLE)


class TestEditDeleteContentCase(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Тестовый текст заметки'
    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls) -> None:

        cls.form = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT}
        cls.new_form = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='test_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.test_note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.edit_note_url = reverse(
            'notes:edit',
            kwargs={
                'slug': cls.test_note.slug
            })
        cls.delete_note_url = reverse(
            'notes:delete',
            kwargs={
                'slug': cls.test_note.slug
            })

    def test_user_cant_edit_note_of_another_user(self):
        self.auth_client.post(
            self.edit_note_url,
            data=self.new_form
        )
        self.test_note.refresh_from_db()
        self.assertEqual(self.test_note.text, self.NOTE_TEXT)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.edit_note_url,
            data=self.new_form
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.test_note.refresh_from_db()
        self.assertEqual(self.test_note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_delete_note_of_another_user(self):
        self.auth_client.delete(
            self.delete_note_url,
        )
        self.test_note.refresh_from_db()
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertEqual(self.test_note.text, self.NOTE_TEXT)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.author_client.delete(
            self.delete_note_url,
        )
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = self.author.notes.count()
        self.assertEqual(notes_count, 0)
