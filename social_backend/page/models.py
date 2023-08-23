from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Page(models.Model):
    name = models.CharField(max_length=80, unique=True)
    owner = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='pages', blank=False)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField('page.Tag', related_name='pages')

    is_private = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='page_follows', blank=True)
    follow_requests = models.ManyToManyField('self',blank=True,related_name='requests_to_follow',symmetrical=False)

    image = models.URLField(null=True, blank=True)
    unblock_date = models.DateTimeField(null=True, blank=True)

    def count_followers(self):
        return self.followers.count()
    
    def count_following(self):
        return Page.objects.filter(followers=self).count()
    
    def __str__(self):
        return f"{self.name}"

class Post(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=280)
    file = models.URLField(null=True, blank=True)

    comments = models.ManyToManyField('Comment', related_name='comments', blank=True)
    reply_to = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True, related_name='replies', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_likes_count(self):
        return self.likes.count()

    def get_dislikes_count(self):
        return self.dislikes.count()

    def __str__(self):
        return self.content
    
class Comment(models.Model):
    content = models.TextField(max_length=180)
    author = models.ForeignKey(Page, on_delete=models.CASCADE, to_field='name')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.created_date}"
    
class Like(models.Model):
    author = models.ForeignKey(Page, on_delete=models.CASCADE, to_field='name', default='Unknown')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

class Dislike(models.Model):
    author = models.ForeignKey(Page, on_delete=models.CASCADE, to_field='name', default='Unknown')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
   
