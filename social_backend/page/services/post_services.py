from rest_framework.response import Response
from account.models import User
from page.models import Page, Post
from django.db.models import Q
from page.producer import send_message

from rest_framework.status import (
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
    HTTP_201_CREATED,
)


def get_feeds(user: User, current_page: Page) -> Response:
    condition = (
        # Обычные посты собственных страниц
        Q(page__owner=user, reply_to__isnull=True, page__unblock_date__isnull=True) |
        # Обычные посты страниц, на которые подписана текущая страница
        Q(page__followers=current_page, reply_to__isnull=True, page__unblock_date__isnull=True) |
        # Посты-репосты собственных страниц
        Q(page__owner=user, reply_to__isnull=False, reply_to__page__is_private=False,
          page__unblock_date__isnull=True)
    )

    if user.role in [User.Roles.MODERATOR, User.Roles.ADMIN]:
        posts = Post.objects.filter(condition)
    else:
        posts = Post.objects.filter(condition)

    return posts.order_by('-created_at')


def repost_post(original_post: Post, current_page: Page) -> Response:
    if current_page.posts.filter(reply_to_id=original_post.id).exists():
        return Response({'detail': 'Repost failed. This post has already been reposted on your page.'},
                        status=HTTP_409_CONFLICT)
    elif original_post.page.is_private:
        return Response({'detail': 'Repost failed. Repost from private page is not allowed.'},
                        status=HTTP_403_FORBIDDEN)
    elif current_page == original_post.page:
        return Response({'detail': 'Repost failed. Reposting your own post is not allowed.'},
                        status=HTTP_403_FORBIDDEN)

    Post.objects.create(
        page=current_page,
        content=original_post.content,
        file=original_post.file,
        reply_to=original_post,
    )
    send_message.delay(
        method="POST",
        body=dict(page_id=original_post.page.pk, action="add_repost"),
    )
    return Response({'detail': 'Reposted successfully.'}, status=HTTP_201_CREATED)


def like_post(post: Post, current_page: Page) -> Response:
    if post.dislikes.filter(author=current_page).first():
        post.dislikes.filter(author=current_page).delete()
        post.likes.create(author=current_page)
        return Response({"message": "Dislike removed, Like added"}, status=201)
    elif post.likes.filter(author=current_page).exists():
        post.likes.filter(author=current_page).delete()
        send_message.delay(
            method="POST",
            body=dict(page_id=post.page.pk, action="remove_like"),
        )
        return Response({"message": "Like removed"}, status=200)
    else:
        post.likes.create(author=current_page)
        send_message.delay(
            method="POST",
            body=dict(page_id=post.page.pk, action="add_like"),
        )
        return Response({"message": "Like added"}, status=201)


def dislike_post(post: Post, current_page: Page) -> Response:
    if post.likes.filter(author=current_page).first():
        post.likes.filter(author=current_page).delete()
        post.dislikes.create(author=current_page)
        send_message.delay(
            method="POST",
            body=dict(page_id=post.page.pk, action="remove_like"),
        )
        return Response({"message": " Like removed, Dislike added"}, status=201)
    elif post.dislikes.filter(author=current_page).exists():
        post.dislikes.filter(author=current_page).delete()
        return Response({"message": "Dislike removed"}, status=200)
    else:
        post.dislikes.create(author=current_page)
        return Response({"message": "Dislike added"}, status=201)
