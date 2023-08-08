from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
    
class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField('page.Tag', related_name='pages')

    owner = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='pages', blank=False)
    followers = models.ManyToManyField('page.Page', through='page.PageFollows', related_name='follows', blank=True)

    image = models.URLField(null=True, blank=True)

    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField('page.Page', related_name='requests', blank=True)

    unblock_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
    
class PageFollows(models.Model):
    from_page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='follows_from')
    to_page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='follows_to')

class Post(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=250)

    likes = models.ManyToManyField('page.Page', related_name="post_likes", blank=True)
    reply_to = models.ForeignKey('page.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.page.name}" f"{self.page}"
    