from django.contrib import admin

from .models import Tag, Page, Post, Comment, Like, Dislike

admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Dislike)


class TagInline(admin.StackedInline):
    model = Tag


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "get_followers_count", "get_following_count", "is_private")

    def get_followers_count(self, obj):
        return obj.count_followers()

    def get_following_count(self, obj):
        return obj.count_following()

    get_followers_count.short_description = 'Followers Count'
    get_following_count.short_description = 'Following Count'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("get_post_id", "page", "get_likes_count", "get_dislikes_count")

    def get_post_id(self, obj):
        return obj.id

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        return obj.dislikes.count()

    get_likes_count.short_description = 'Likes'
    get_dislikes_count.short_description = 'Dislikes'
    get_post_id.short_description = 'Post ID'
