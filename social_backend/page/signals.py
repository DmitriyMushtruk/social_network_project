from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment


@receiver(post_save, sender=Comment)
def create_page_post_comment(sender, instance, created, **kwargs):
    if created and instance.post:
        instance.post.comments.add(instance)
