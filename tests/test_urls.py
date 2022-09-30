from http import client
from django.test import TestCase, Client
from blog.models import Post, Tag, Comment
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import reverse 

TAG_TITLE = 'tag_title'
POST_SLUG = 'post_slug'
HOMEPAGE = reverse('index')
TAGPAGE = reverse(
    'tag_filter',
    args=[TAG_TITLE],
)
POSTPAGE = reverse(
    'post_detail',
    args=[POST_SLUG],
)
CONTACTSPAGE = reverse('contacts')
HOMEPAGE_TEMPLATE = 'index.html'
CONTACTS_TEMPLATE = 'contacts.html'
POST_TEMPLATE = 'post_details.html'
TAG_TEMPLATE = 'posts-list.html'


class TestBlogUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = Tag.objects.create(title=TAG_TITLE)
        cls.user = User.objects.create(username='User_for_test')
        cls.post = Post.objects.create(
            title='Post_for_test',
            text='Text_in_post',
            published_at=datetime.today(),
            author=cls.user,
            slug=POST_SLUG,
        )
        cls.guest_client = Client()


    def test_url_exists_at_desired_location(self):
        """
        Проверка статуса страницы.
        """
        app_urls = (
            (self.guest_client, HOMEPAGE, 200),
            (self.guest_client, TAGPAGE, 200),
            (self.guest_client, POSTPAGE, 200),
            (self.guest_client, CONTACTSPAGE, 200),
        )
        for client, url, status in app_urls: 
            with self.subTest(url=url): 
                self.assertEqual(client.get(url).status_code, status) 
    
    def test_template(self):
        """
        Проверка шаблона по url.
        """
        templates_urls = (
            (HOMEPAGE, HOMEPAGE_TEMPLATE),
            (POSTPAGE, POST_TEMPLATE),
            (TAGPAGE, TAG_TEMPLATE),
            (CONTACTSPAGE, CONTACTS_TEMPLATE),
        )
        for url, template in templates_urls: 
            with self.subTest(url=url): 
                self.assertTemplateUsed(
                    self.guest_client.get(url), 
                    template,
                )
