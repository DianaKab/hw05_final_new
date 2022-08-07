from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='username')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id='1',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_status_code(self):
        templates_pages_names = {
            '/':
            HTTPStatus.OK,
            '/group/test-slug/':
            HTTPStatus.OK,
            '/profile/HasNoName/':
            HTTPStatus.OK,
            '/posts/1/':
            HTTPStatus.OK,
            '/unexisting_page/':
                HTTPStatus.NOT_FOUND,
            '/create/':
                HTTPStatus.FOUND
        }

        for reverse_name, httpstatus_code in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, httpstatus_code)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
