from django.db.models import Count, F, Prefetch
from django.shortcuts import render

from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_amount,
    }


def index(request):
    """Перенаправление на главную страницу
    с содержанием 5 самых популярных постов,
    5 последних опубликованных постов
    и 5 самых популярных тегов.
    """
    most_popular_posts = Post.objects.popular()[:5] \
                                     .prefetch_related('author') \
                                     .prefetch_related(Prefetch(
                                        'tags',
                                        queryset=Tag.objects.annotate(
                                            posts_amount=Count('posts'),
                                        ))) \
                                     .fetch_with_comments_count()

    most_fresh_posts = Post.objects.prefetch_related('author') \
                           .prefetch_related(Prefetch(
                                'tags',
                                queryset=Tag.objects.annotate(
                                    posts_amount=Count('posts'),
                                ))) \
                           .annotate(comments_amount=Count('comments')) \
                           .order_by('-published_at')[:5]

    most_popular_tags = Tag.objects.popular()[:5] \
                                   .annotate(posts_amount=Count('posts'))

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    """Страница поста с переданным slug
    количество лайков под постом, связанные теги
    и комментарии к посту.
    """

    post = Post.objects.prefetch_related(Prefetch(
                            'comments',
                            queryset=Comment.objects.annotate(
                                author_name=F('author__username'),
                            ))) \
                       .prefetch_related(Prefetch(
                            'tags',
                            queryset=Tag.objects.annotate(
                                posts_amount=Count('posts')),
                            )) \
                       .annotate(likes_amount=Count('likes')) \
                       .select_related('author') \
                       .get(slug=slug)

    comments = post.comments.all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author_name
        })

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5] \
                                   .annotate(posts_amount=Count('posts'))
    most_popular_posts = Post.objects.popular()[:5] \
                                     .prefetch_related('author') \
                                     .prefetch_related(Prefetch(
                                        'tags',
                                        queryset=Tag.objects.annotate(
                                            posts_amount=Count('posts'),
                                        ))) \
                                     .fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    """Страница тега с переданным заголовком
    5 самых популярных тегов
    5 самых популярных постов
    посты, связанные с тегом.
    """
    tag = Tag.objects.prefetch_related('posts') \
                     .get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects.popular()[:5] \
                                     .prefetch_related('author') \
                                     .prefetch_related(Prefetch(
                                        'tags',
                                        queryset=Tag.objects.annotate(
                                            posts_amount=Count('posts'),
                                        ))) \
                                     .fetch_with_comments_count()

    related_posts = tag.posts.annotate(comments_amount=Count('comments')) \
                             .prefetch_related('author') \
                             .prefetch_related(Prefetch(
                                'tags',
                                queryset=Tag.objects.annotate(
                                    posts_amount=Count('posts'),
                                )
                             ))

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
