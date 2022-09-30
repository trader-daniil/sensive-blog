from django.test import TestCase
from blog.models import Post, Tag, Comment
from django.contrib.auth.models import User
from datetime import datetime


class TestBlogModels(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = Tag.objects.create(title='Tag_for_test')
        cls.user = User.objects.create(username='User_for_test')
        cls.post = Post.objects.create(
            title='Post_for_test',
            text='Text_in_post',
            published_at=datetime.today(),
            author=cls.user,
        )
        cls.post.likes.add(cls.user)
        cls.post.tags.add(cls.tag)
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Text_in_comment',
            published_at=datetime.today(),
            post=cls.post,
        )

    def test_tag_fields(self):
        """
        Проверяем значения полей тега.
        """
        post = TestBlogModels.post
        tag = TestBlogModels.tag
        self.assertEqual(
            tag.title,
            'Tag_for_test',
        )
        self.assertIn(
            post,
            tag.posts.all()
        )
    
    def test_post_fields(self):
        """
        Проверяем значениия полей поста.
        """
        post = TestBlogModels.post
        user = TestBlogModels.user
        tag = TestBlogModels.tag
        post_fields_values = {
            'title': 'Post_for_test',
            'text': 'Text_in_post',
            'author': user,
        }
        for field, expected_value in post_fields_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(
                        post,
                        field,
                    ),
                    expected_value,
                )
        self.assertIn(
            tag,
            post.tags.all(),
        )
        self.assertIn(
            user,
            post.likes.all(),
        )
    
    def test_comment_fields(self):
        """
        Проверяем значения комментария.
        """
        post = TestBlogModels.post
        user = TestBlogModels.user
        comment = TestBlogModels.comment
        comment_fields_values = {
            'text': 'Text_in_comment',
            'post': post,
            'author': user,
        }
        for field, expected_value in comment_fields_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(
                        comment,
                        field,
                    ),
                    expected_value,
                )
