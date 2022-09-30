from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.text import slugify

class PostQuerySet(models.QuerySet):

    def year(self, year):
        """Возвращает посты, написанные в указанный год."""
        posts_at_sended_year = self.filter(published_at__year=year) \
                                   .order_by('published_at')
        return posts_at_sended_year

    def popular(self):
        """Возвращает посты, отсортированные по убыванию популярности."""
        most_popular_posts = self.annotate(likes_amount=Count('likes')) \
                                 .order_by('-likes_amount')
        return most_popular_posts

    def fetch_with_comments_count(self):
        """Возвращает посты с количеством комментариев
        Принимает объект post, для которого посчитаны лайки,
        после создаем поле comments_amount для переданных записей
        работает быстрее двух annotate.
        """
        most_popular_posts_id = [post.id for post in self]
        posts_with_comments = Post.objects.filter(
            id__in=most_popular_posts_id) \
                                          .annotate(
                                            comments_count=Count('comments'),
                                          )
        posts_with_comments = posts_with_comments.values_list(
            'id',
            'comments_count',
        )
        posts_with_comments = dict(posts_with_comments)
        for post in self:
            post.comments_amount = posts_with_comments[post.id]
        return self


class TagQuerySet(models.QuerySet):

    def popular(self):
        """Возвращает теги по убыванию число связанных постов."""
        tags_with_popularity = self.annotate(
            posts_amount=Count('posts')).order_by('-posts_amount')
        return tags_with_popularity


class Post(models.Model):
    """
    Модель поста.
    """
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
    )
    text = models.TextField(verbose_name='Текст')
    slug = models.SlugField(
        verbose_name='Название в виде url',
        max_length=200,
    )
    image = models.ImageField(verbose_name='Картинка')
    published_at = models.DateTimeField(verbose_name='Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True},
    )
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True,
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги',
    )
    objects = PostQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
        

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    """
    Модель Тега, по которому ищут посты в БД.
    """
    title = models.CharField(
        verbose_name='Тег',
        max_length=20,
        unique=True,
    )
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    """
    Модель комментраия к посту
    """
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )

    text = models.TextField(verbose_name='Текст комментария')
    published_at = models.DateTimeField(verbose_name='Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
