from django.contrib import admin

from .models import Tag, Page, Post, Comment, Like, Dislike

admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Dislike)

class TagInline(admin.StackedInline):
    model = Tag

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "owner","get_followers_count", "get_following_count", "is_private")

    def get_followers_count(self, obj):
        return obj.count_followers()
    
    def get_following_count(self, obj):
        return obj.count_following()

    get_followers_count.short_description = 'Followers Count'
    get_following_count.short_description = 'Following Count'