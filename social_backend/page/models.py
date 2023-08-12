from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Page(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='pages', blank=False)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField('page.Tag', related_name='pages')

    is_private = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='page_follows', blank=True)
    follow_requests = models.ManyToManyField('self',blank=True,related_name='requests_to_follow',symmetrical=False)

    image = models.URLField(null=True, blank=True)
    unblock_date = models.DateTimeField(null=True, blank=True)

    #Get number of page followers
    def count_followers(self):
        return self.followers.count()
    
    #Get number of page follows
    def count_following(self):
        return Page.objects.filter(followers=self).count()
    
    def __str__(self):
        return f"{self.name}"