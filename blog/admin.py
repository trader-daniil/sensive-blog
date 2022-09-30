from django.contrib import admin

from blog.models import Comment, Post, Tag


@admin.register(Post)
class AdminPost(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'slug',
        'published_at',
    )
    search_fields = (
        'text',
        'slug',
    )
    raw_id_fields = (
        'likes',
        'tags',
    )


class PostInstance(admin.TabularInline):
    model = Post.tags.through
    raw_id_fields = ('post',)


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('title',)
    inlines = (PostInstance,)


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    list_display = (
        'text',
        'published_at',
    )
    readonly_fields = (
        'published_at',
    )
    raw_id_fields = (
        'post',
        'author',
    )
