from celery import shared_task
from social_backend import settings

from page.models import Post
from django.core.mail import send_mail


@shared_task
def send_new_post_notification_email(post_id: int) -> None:
    post = Post.objects.get(pk=post_id)

    recipients_emails = []
    for page in post.page.followers.all():
        if (page.owner.email
                not in recipients_emails
                and not page.owner.is_blocked):
            recipients_emails.append(page.owner.email)

    subject = f'Check out new post by {post.page.owner.username}'
    message = f'New post is available on {post.page.name} page! \U0001F680'
    from_email = settings.EMAIL_HOST_USER

    send_mail(subject, message, from_email, recipients_emails, fail_silently=False)
