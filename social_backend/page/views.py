from rest_framework import status, viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from rest_framework.mixins import (
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)

from page.serializers.page_serializer import (
    TagListSerializer,
    PostSerializer,
    PageSerializer,
    CommentSerializer,
)

from page.page_permissions import ( 
    IsOwner,
    CheckCurrentPage,
    CanViewPage,
    IsAdminOrModer,
    CanViewPost,
    CheckPageBlockStatus,
)

from page.services import (
    follow_unfollow,
    approve_request,
    approve_all_requests,
    reject_request,
    reject_all_requests,
    get_page_posts,
    repost_post,
    like_post,
    dislike_post,
    )

from account.models import User
from page.models import Page, Tag, Post, Comment

# Блокироовка пользователей должна быть доступна админам.
# Убрать возможность репостить один и тот же пост несколько раз одной и той же страницей
class TagListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer
    permission_classes = (IsAuthenticated)

class UserPageListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated)
    lookup_field = "name"

    def get_queryset(self):
        return Page.objects.filter(owner=self.request.user)

class PageViewSet(
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet
    ):

    """Page ViewSet"""

    queryset = Page.objects.prefetch_related("tags").all()
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated, CheckPageBlockStatus]
    lookup_field = "name"

    def get_permissions(self):
        if self.action in ('update', 'destroy', 'approve_requests_action', 'reject_requests_action', 'get_requests_action'):
            self.permission_classes += [IsOwner]
        elif self.action in ('block_action', 'unblock_action'):
            self.permission_classes += [IsAdminOrModer]
        elif self.action ==  'follow_unfollow_action':
            self.permission_classes += [CheckCurrentPage]
        else:
            self.permission_classes += [(CanViewPage | IsOwner)]

        return super(PageViewSet, self).get_permissions()
    
    @action(
            detail=True,
            methods=['post'],
            url_name="follow_unfollow",
            url_path="follow_unfollow",
    )
    def follow_unfollow_action(self, request, name=None):
        """This action allows users to follow or unfollow pages"""
        self.check_permissions(self.request)
        current_page = Page.objects.get(id=request.query_params.get('current_page'))
        return follow_unfollow(current_page, self.get_object(), request.user)
    
    @action(
        detail=True,
        methods=['post'],
    )
    def approve_requests_action(self, request, name, *args, **kwargs):
        """
        This action allows the private page owner to accept follow requests.
        One at a time or all at once
        """
        self.check_permissions(self.request)
        page = get_object_or_404(Page, name=name)
        if kwargs.get("requester_page"):
            requester = get_object_or_404(Page, id=kwargs.get("requester_page"))
            return approve_request(page, requester)
        return approve_all_requests(page)

    @action(
        detail=True,
        methods=['post'],
    )
    def reject_requests_action(self, request, name, *args, **kwargs):
        """
        This action allows the private page owner to reject follow requests.
        One at a time or all at once
        """
        self.check_permissions(self.request)
        page = get_object_or_404(Page, name=name)
        if kwargs.get("requester_page"):
            requester = get_object_or_404(Page, id=kwargs.get("requester_page"))
            return reject_request(page, requester)
        return reject_all_requests(page)
    
    @action(
            detail=True,
            methods=['get']
    )
    def get_requests_action(self, request, name):
        """
        This action allows the owner of the page to see the list of pages who want to follow his page.
        """
        self.check_permissions(self.request)
        page = get_object_or_404(Page, name=name)
        requesters = page.follow_requests.all()
        serializer = PageSerializer(requesters, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['get'],
    )
    def get_followers_action(self, request, pk=None, name=None):
        """This action allows you to view the list of subscribers of a particular page"""
        self.check_permissions(self.request)
        page = get_object_or_404(Page.objects.all(), name=name)
        self.check_object_permissions(self.request, page)
        followers = page.followers.all()
        serializer = PageSerializer(followers, many=True)
        return Response(serializer.data)
    
    @action(
        detail=True,
        methods=['post'],
        url_name="block",
        url_path="block",
    )
    def block_action(self, request, name):
        """This action allows administrators and moderators to block pages for a certain amount of time."""
        self.check_permissions(self.request)
        page = get_object_or_404(Page.objects.all(), name=name)
        page.unblock_date = request.data.get('unblock_date')
        page.save()

        return Response({'detail': 'Page has been blocked.'}, status=status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['post'],
        url_name="unblock",
        url_path="unblock",
    )
    def unblock_action(self, request, name):
        """This action allows administrators and moderators to unblock pages"""
        self.check_permissions(self.request)
        page = get_object_or_404(Page.objects.all(), name=name)
        page.unblock_date = None
        page.save()

        return Response({'detail': 'Page has been unblocked.'}, status=status.HTTP_200_OK)
    

class PostViewSet(
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet):

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes += [(IsOwner | IsAdminOrModer | CanViewPost and CheckCurrentPage)]
        elif self.action == 'destroy':
            self.permission_classes += [(IsOwner | IsAdminOrModer)]
        elif self.action == 'update':
            self.permission_classes += [IsOwner]
        elif self.action == 'create':
            self.permission_classes += [CheckCurrentPage]
        elif self.action == 'get_page_posts_action':
            self.permission_classes += [CanViewPage]
        elif self.action == 'get_liked_posts_action':
            self.permission_classes += [CheckCurrentPage]
        elif self.action in ('comment_action', 'repost_action', 'like_action', 'dislike_action',):
            self.permission_classes += [CanViewPost and CheckCurrentPage]

        return super(PostViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        current_page = Page.objects.get(id=request.query_params.get('current_page'))
        request.data['page'] = current_page.pk
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        serializer = self.serializer_class(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(
        detail=True,
        methods=['get']
    )
    def get_page_posts_action(self, request, *args, **kwargs):
        page = get_object_or_404(Page.objects.all(), name=self.kwargs['name'])
        self.check_object_permissions(request, page)
        user = self.request.user
        current_page = request.query_params.get('current_page')
        posts = get_page_posts(page, user, current_page)
        serializer = PostSerializer(posts, many = True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post']
    )
    def comment_action(self, request, name=None, pk=None):
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))
        post = get_object_or_404(Post, pk=pk)
        comment_text = request.data.get('content')
        comment = Comment.objects.create(post=post, author=current_page, content=comment_text)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(
        detail=True,
        methods=['post']
    )
    def repost_action(self, request, pk=None):
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))
        original_post = get_object_or_404(Post, pk=pk)

        return repost_post(original_post, current_page)

    @action(
        detail=True,
        methods=['post'],
    )
    def like_action(self, request, pk=None):
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))
        post = get_object_or_404(Post, pk=pk)
        return like_post(post, current_page)
        
    @action(
        detail=True,
        methods=['post']
    )
    def dislike_action(self, request, pk=None):
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))
        post = get_object_or_404(Post, pk=pk)
        return dislike_post(post, current_page)
       
    # Убрать пост из списка, если страница поста заблокирована
    @action(
        detail=False,
        methods=['GET'],
        url_name="liked",
        url_path='liked'
    )
    def get_liked_posts_action(self, request, pk=None):
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))
        liked_posts = Post.objects.filter(likes__author=current_page)
        serializer = self.get_serializer(liked_posts, many=True)
        return Response(serializer.data)

class FeedView(APIView):
    permission_classes = [IsAuthenticated, CheckCurrentPage]
    
    def get(self, request):
        user = request.user
        current_page = Page.objects.get(id=request.query_params.get('current_page'))
        followed_pages = current_page.page_follows.all()
        own_pages = Page.objects.filter(owner=request.user)
        pages = followed_pages | own_pages

        feeds_posts = []
        for page in pages:
            if page.unblock_date == None:
                posts = get_page_posts(page, user, current_page)
                feeds_posts.extend(posts)
        
        sorted_feeds_posts = sorted(feeds_posts, key=lambda x: x.created_at, reverse=True)

        serializer = PostSerializer(sorted_feeds_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)