from rest_framework.response import Response
from account.models import User
from page.models import Page, Post
from django.db.models import Q
from django.db import connection
from django.http import HttpResponse

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
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
    
def reject_all_requests(page: Page) -> Response:
    requesters = page.follow_requests.all()
    for requester in requesters:
        page.follow_requests.remove(requester)
    return Response({'detail': 'All requests reject successfully.'}, status=HTTP_200_OK)

def get_page_posts(page: Page, user: User, current_page: Page) -> Response:
    condition = (
        Q(page=page, reply_to__isnull=True, page__unblock_date__isnull=True) |  # Обычные посты на странце
        Q(page=page, reply_to__isnull=False, reply_to__page__unblock_date__isnull=True) & ~Q(reply_to__page=page)  # Репосты из открытых страниц
    )

    if user.role not in [User.Roles.MODERATOR, User.Roles.ADMIN]:
        posts = Post.objects.filter(condition)
    else:
        posts = Post.objects.filter(page=page)

    return posts.order_by('-created_at')

def page_or_user_search(query) -> Response:
    query = str(query)
    sql = """
    SELECT id::text, name, description, 'page' AS object_type
    FROM page_page
    WHERE name ILIKE %s OR description ILIKE %s

    UNION ALL

    SELECT id::text, username AS name, '' AS description, 'user' AS object_type
    FROM account_user
    WHERE username ILIKE %s

    UNION ALL
    
    SELECT p.id::text, p.name, p.description, 'page' AS object_type
    FROM page_page AS p
    INNER JOIN page_page_tags AS pt ON p.id = pt.page_id
    INNER JOIN page_tag AS t ON pt.tag_id = t.id
    WHERE t.name ILIKE %s
    """

    params = [f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%']
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        results = cursor.fetchall()
    
    if len(results) == 0:
        return HttpResponse('Not found', status=404)
    
    queryset = []
    
    for row in results:
        print("Row: ", row)
        if len(row) >= 4 and row[3] == 'user':
            queryset.append(User(id=row[0], username=row[1]))
        elif len(row) >= 4 and row[3] == 'page':
            queryset.append(Page(id=row[0], name=row[1], description=row[2]))
        
    if not queryset:
        return HttpResponse('Not found', status=404)

    return queryset