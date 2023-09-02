from rest_framework.response import Response
from rest_framework.request import Request
from account.models import User
from page.models import Page, Post
from django.utils import timezone

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
    HTTP_201_CREATED,
)

def follow_unfollow(current_page: Page, page = Page, user = User) -> Response:
    if page in user.pages.all():
        return Response(
            {"response": "You're can't follow your own page"},
            status=HTTP_409_CONFLICT,
        )

    if current_page in page.followers.all():
        page.followers.remove(current_page)
        return Response({"detail": "Unfollowed successfully."},status=HTTP_200_OK,)
    else:
        if page.is_private:
            if not current_page in page.follow_requests.all():
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
    
def reject_all_requests(page: Page, user: User) -> Response:
    requesters = page.follow_requests.all()
    for requester in requesters:
        page.follow_requests.remove(requester)
    return Response({'detail': 'All requests reject successfully.'}, status=HTTP_200_OK)

def get_page_posts(page: Page, user: User, current_page: Page) -> Response:
    posts = Post.objects.filter(page=page)
    if user.role == User.Roles.MODERATOR or user.role == User.Roles.ADMIN:
        return posts
    else:
        filtred_posts = []
        for post in posts:
            if post.reply_to is not None:
                original_post = Post.objects.get(id=post.reply_to.id)
                if (
                    original_post.page.is_private
                    and original_post.page.followers.filter(id=current_page.id).exists()
                    and original_post.page.unblock_date == None
                    ):
                    filtred_posts.append(post)
                elif (
                    not original_post.page.is_private
                    and original_post.page.unblock_date == None
                    ):
                    filtred_posts.append(post)
                elif original_post.page.owner == user:
                    filtred_posts.append(post)
            elif page.is_private and page.followers.filter(id=current_page.id).exists():
                filtred_posts.append(post)
            else:
                filtred_posts.append(post)
        return filtred_posts

def repost_post(original_post: Post, current_page: Page) -> Response:
    if current_page.posts.filter(id=original_post.id).exists():
            return Response({'detail': 'Repost failed.'}, status=HTTP_201_CREATED)

    reposted_post = Post.objects.create(
    page=current_page,
    content=original_post.content,
    file=original_post.file,
    reply_to=original_post,
    )
    return Response({'detail': 'Reposted successfully.'}, status=HTTP_201_CREATED)

def like_post(post: Post, current_page: Page) -> Response:
    if post.dislikes.filter(author=current_page).first():
            post.dislikes.filter(author=current_page).delete()
            post.likes.create(author=current_page)
            return Response({"message": "Dislike removed, Like added"}, status=201)
    elif post.likes.filter(author=current_page).exists():
        post.likes.filter(author=current_page).delete()
        return Response({"message": "Like removed"}, status=200)
    else:
        post.likes.create(author=current_page)
        return Response({"message": "Like added"}, status=201)
    
def dislike_post(post: Post, current_page: Page) -> Response:
    if post.likes.filter(author=current_page).first():
            post.likes.filter(author=current_page).delete()
            post.dislikes.create(author=current_page)
            return Response({"message": " Like removed, Dislike added"}, status=201)
    elif post.dislikes.filter(author=current_page).exists():
        post.dislikes.filter(author=current_page).delete()
        return Response({"message": "Dislike removed"}, status=200)
    else:
        post.dislikes.create(author=current_page)
        return Response({"message": "Dislike added"}, status=201)

