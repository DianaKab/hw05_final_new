import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

FISRT_PAGE = 10
SECOND_PAGE1 = 6
SECOND_PAGE2 = 1
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='username')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug_2',
            description='Тестовое описание_2',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group_1,
            id='1',
            image=cls.uploaded,
        )
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'username'}):
                'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 1}):
                'posts/post_detail.html',
            reverse(
                'posts:post_create'):
                'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': 1}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сгенерирован с верным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        image_object = first_object.image
        post_author_0 = first_object.author.username
        self.assertEqual(str(first_object),
                         'Тестовый пост')
        self.assertEqual(post_author_0, 'username')
        self.assertEqual(image_object, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сгенерирован с верным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        )
        )
        post_object = response.context['page_obj'][0]
        group_object = response.context['group']
        image_object = post_object.image
        post_group = group_object.title
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(image_object, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сгенерирован с верным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'username'})
        )
        profile_object = response.context['page_obj'][0]
        image_object = profile_object.image
        post_author_0 = profile_object.author.username
        self.assertEqual(post_author_0, 'username')
        self.assertEqual(image_object, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сгенерирован с верным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': 1})
        )
        post_detail_object = response.context['post']
        image_object = post_detail_object.image
        self.assertEqual(post_detail_object.pk, 1)
        self.assertEqual(image_object, 'posts/small.gif')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сгенерирован с верным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create')
        )
        form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сгенерирован с верным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create_user(username='username_1')

        cls.user_2 = User.objects.create_user(username='username_2')

        cls.group_1 = Group.objects.create(
            title='Тестовая группа_1',
            slug='test-slug_1',
            description='Тестовое описание_1',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug_2',
            description='Тестовое описание_2',
        )

        for i in range(11):
            cls.post = Post.objects.create(
                author=cls.user_1,
                text=f'Тестовый пост {i}',
                group=cls.group_1,
            )

        for i in range(5):
            cls.post = Post.objects.create(
                author=cls.user_2,
                text=f'Тестовый пост {i}',
                group=cls.group_2,
            )

        cls.anon_client = Client()
        cls.client_1 = Client()
        cls.client_1.force_login(cls.user_1)
        cls.client_2 = Client()
        cls.client_2.force_login(cls.user_2)

    def test_first_page_contains_ten_records(self):
        response = self.anon_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), FISRT_PAGE)

    def test_second_page_contains_six_records(self):
        response = self.anon_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), SECOND_PAGE1)

    def test_first_page_filter_by_group(self):
        response = self.anon_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug_1'})
        )
        self.assertEqual(len(response.context['page_obj']), FISRT_PAGE)

    def test_second_page_filter_by_group(self):
        response = self.anon_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug_1'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), SECOND_PAGE2)

    def test_first_page_filter_by_profile(self):
        response = self.anon_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'username_1'})
        )
        self.assertEqual(len(response.context['page_obj']), FISRT_PAGE)

    def test_second_page_filter_by_profile(self):
        response = self.anon_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'username_1'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), SECOND_PAGE2)

    def test_cache_index_page(self):
        response1 = self.anon_client.get(reverse('posts:index'))
        self.post.delete()
        response2 = self.anon_client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.anon_client.get(reverse('posts:index'))
        self.assertNotEqual(response1.content, response3.content)


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "core/404.html")


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower')
        self.user_following = User.objects.create_user(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовый пост'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        self.client_auth_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'following'}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        self.client_auth_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'following'}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription(self):
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.client_auth_follower.get(
            reverse(
                'posts:follow_index'
            )
        )
        post_text = response.context['page_obj'][0].text
        self.assertEqual(post_text, self.post.text)
        response = self.client_auth_following.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertNotContains(response, self.post.text)
