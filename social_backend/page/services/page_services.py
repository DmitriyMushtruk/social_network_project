from rest_framework.response import Response
from account.models import User
from page.models import Page, Post
from django.db.models import Q

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)


def follow_unfollow(current_page: Page, page=Page, user=User) -> Response:
    if page in user.pages.all():
        return Response(
            {"response": "You're can't follow your own page"},
            status=HTTP_409_CONFLICT,
        )

    if current_page in page.followers.all():
        page.followers.remove(current_page)
        return Response({"detail": "Unfollowed successfully."}, status=HTTP_200_OK, )
    else:
        if page.is_private:
            if current_page not in page.follow_requests.all():
                page.follow_requests.add(current_page)
                return Response({'detail': 'Follow request sent successfully.'}, status=HTTP_200_OK)
            else:
                page.follow_requests.remove(current_page)
                return Response({'detail': 'Follow request canceled successfully.'}, status=HTTP_200_OK)
        else:
            page.followers.add(current_page)
            return Response({'detail': 'Followed successfully.'}, status=HTTP_200_OK)


def approve_request(page: Page, requester: Page) -> Response:
    if requester in page.follow_requests.all():
        page.followers.add(requester)
        page.follow_requests.remove(requester)
        return Response({'detail': 'Request approved successfully.'}, status=HTTP_200_OK)
    else:
        return Response({'detail': 'Follow request not found.'}, status=HTTP_404_NOT_FOUND)


def approve_all_requests(page: Page) -> Response:
    requesters = page.follow_requests.all()
    for requester in requesters:
        page.followers.add(requester)
        page.follow_requests.remove(requester)
    return Response({'detail': 'All requests approved successfully.'}, status=HTTP_200_OK)


def reject_request(page: Page, requester: Page) -> Response:
    if requester in page.follow_requests.all():
        page.follow_requests.remove(requester)
        return Response({'detail': 'Request reject successfully.'}, status=HTTP_200_OK)
    else:
        return Response({'detail': 'Follow request not found.'}, status=HTTP_404_NOT_FOUND)


def reject_all_requests(page: Page) -> Response:
    requesters = page.follow_requests.all()
    for requester in requesters:
        page.follow_requests.remove(requester)
    return Response({'detail': 'All requests reject successfully.'}, status=HTTP_200_OK)


def get_page_posts(page: Page, user: User) -> Response:
    condition = (
        Q(page=page, reply_to__isnull=True, page__unblock_date__isnull=True) |  # Обычные посты на странце
        Q(page=page, reply_to__isnull=False, reply_to__page__unblock_date__isnull=True) & ~Q(reply_to__page=page)
        # Репосты из открытых страниц
    )

    if user.role not in [User.Roles.MODERATOR, User.Roles.ADMIN]:
        posts = Post.objects.filter(condition)
    else:
        posts = Post.objects.filter(page=page)

    return posts.order_by('-created_at')


def page_or_user_search(query):
    if not isinstance(query, str):
        return []

    query = str(query)

    page_results = Page.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    user_results = User.objects.filter(username__icontains=query)
    tag_results = Page.objects.filter(tags__name__icontains=query)

    queryset = list(page_results) + list(user_results) + list(tag_results)

    return queryset
