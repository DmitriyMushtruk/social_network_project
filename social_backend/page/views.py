from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import status

from .models import Page, Tag, Post, Comment
from .serializers import page_serializer
from . import page_permissions
from .mixins import CheckCurrentPageMixin

class TagListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = page_serializer.TagListSerializer
    permission_classes = (permissions.AllowAny,)

class UserPageListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = page_serializer.PageSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = "name"

    def get_queryset(self):
        return Page.objects.filter(owner=self.request.user)

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = page_serializer.PageSerializer
    lookup_field = "name"

    def get_queryset(self):
        try:
            current_page_id = self.request.query_params.get('current_page')
            current_page = Page.objects.get(id=current_page_id)
        except Page.DoesNotExist:
            raise NotFound({"detail": "Page not found - 'current_page' is incorrect."})
        
        if not page_permissions.IsOwner().has_object_permission(self.request, self, current_page):
            raise PermissionDenied({'detail': 'You are not the owner of this page.'})
        
        name = self.kwargs.get('name')
        page = Page.objects.filter(name=name).first()

        if page == None:
            raise NotFound({"detail": "Page not found"})
        
        posts = Post.objects.filter(page=page)

        visible_posts = []
        for post in posts:
            if post.reply_to is not None:
                original_post = Post.objects.get(id=post.reply_to_id)
                if page_permissions.PostsPermissionsSet().has_object_permission(self.request, self, original_post):
                    visible_posts.append(post)
            else:
                visible_posts.append(post)

        self.visible_posts = visible_posts
        return page

    # Добавить сюда пермишены и интегрировать в код, если имееть смысл
    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [page_permissions.IsOwner()]
        return super().get_permissions()
        
    def retrieve(self, request, *args, **kwargs):
        page = self.get_queryset()

        if not page_permissions.CanViewPage().has_object_permission(request, self, page):
            return Response({'detail': 'You are do not have permisiions to view this content. Must be: follower, owner, admin/moder.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            page = self.get_queryset()
            serializer = page_serializer.PageSerializer(page, context={'visible_posts': self.visible_posts})
            return Response(serializer.data)
        except Page.DoesNotExist:
            return Response({'detail': 'Page not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        page = self.get_queryset()

        if not page_permissions.IsOwner().has_object_permission(request, self, page):
            return Response({'detail': 'You are not the owner of this page.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(page, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(page, '_prefetched_objects_cache', None):
            page._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        page = self.get_queryset()

        if not page_permissions.IsOwner().has_object_permission(request, self, page):
            return Response({'detail': 'You are not the owner of this page.'}, status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(page)
        return Response({"detail": "Page deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['post'])
    def follow(self, request, name=None):
        page = self.get_queryset()

        current_page = Page.objects.get(id=request.query_params.get('current_page'))
        
        if page.is_private:
            page.follow_requests.add(current_page)
            return Response({'detail': 'Follow request sent successfully.'}, status=status.HTTP_200_OK)
        
        if page.followers.filter(id=current_page.id).exists():
            return Response({'detail': 'You are already following this page.'}, status=status.HTTP_400_BAD_REQUEST)

        page.followers.add(current_page)
        return Response({'detail': 'Followed successfully.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, name=None):
        page = self.get_queryset()

        current_page = Page.objects.get(id=request.query_params.get('current_page'))

        if not page.followers.filter(id=current_page.id).exists():
            return Response({'detail': 'You are not following this page.'}, status=status.HTTP_400_BAD_REQUEST)

        page.followers.remove(current_page)
        return Response({'detail': 'Unfollowed successfully.'}, status=status.HTTP_200_OK)

    # Это работает (вроде) но думаю можно было бы скоротить, типо если в url указано approve то добавить 
    # если reject то удалить запрос. Что-то в таком духе. Потому что по сути сейчас approve_request и reject_request
    # отличаються лишь одной строкой. 
    @action(detail=True, methods=['post'], url_path='requests/approve/(?P<id_page>\d+)/')
    def approve_request(self, request, name=None, id_page=None):
        page = self.get_queryset()

        if not page_permissions.IsOwner().has_object_permission(request, self, page):
            return Response({'detail': 'You are not the owner of this page.1'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            requester_page = Page.objects.get(id=id_page)
        except Page.DoesNotExist:
            return Response({'detail': 'Requested page not found.'}, status=status.HTTP_404_NOT_FOUND)

        if page:
            if requester_page in page.follow_requests.all():
                page.followers.add(requester_page)
                page.follow_requests.remove(requester_page)
                return Response({'detail': 'Request approved successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Follow request not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'Page not found.'}, status=404)

    @action(detail=True, methods=['post'], url_path='requests/reject/(?P<id_page>\d+)/')
    def reject_request(self, request, name=None, id_page=None):
        page = self.get_queryset()

        if not page_permissions.IsOwner().has_object_permission(request, self, page):
            return Response({'detail': 'You are not the owner of this page.1'}, status=status.HTTP_403_FORBIDDEN)

        try:
            requester_page = Page.objects.get(id=id_page)
        except Page.DoesNotExist:
            return Response({'detail': 'Requested page not found.'}, status=status.HTTP_404_NOT_FOUND)

        if page:
            if requester_page in page.follow_requests.all():
                page.follow_requests.remove(requester_page)
                return Response({'detail': 'Request rejected successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Follow request not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'Page not found.'}, status=404)

class PostViewSet(CheckCurrentPageMixin, viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = page_serializer.PostSerializer

    def list(self, request, *args, **kwargs):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        current_page_id = request.query_params.get('current_page')

        posts = self.queryset.filter(page=current_page_id).order_by('-created_at')
        serializer = self.serializer_class(posts, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            post = self.queryset.get(pk=kwargs['pk'])
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if not page_permissions.PostsPermissionsSet().has_object_permission(request, self, post):
            return Response({'detail': 'You do not have permissions to view this content. Must be: follower, owner, admin/moder.'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.serializer_class(post)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        current_page_id = request.query_params.get('current_page')

        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        current_page = Page.objects.get(id=current_page_id)
        
        request.data['page'] = current_page.pk
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        try:
            post = self.queryset.get(pk=kwargs['pk'])
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)

        try:
            post = self.queryset.get(pk=kwargs['pk'])
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        post.delete()
        return Response({'detail': 'Post has been deleted.'}, status=status.HTTP_204_NO_CONTENT)
    def comment(self, request, name=None, pk=None):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))

        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not page_permissions.PostsPermissionsSet().has_object_permission(request, self, post):
            return Response({'detail': 'You do not have permissions to create content on this page. Must be: follower, owner, admin/moder.'}, status=status.HTTP_403_FORBIDDEN)
        
        comment_text = request.data.get('content')
        comment = Comment.objects.create(post=post, author=current_page, content=comment_text)
        serializer = page_serializer.CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def repost(self, request, pk=None):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))

        try:
            original_post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not page_permissions.PostsPermissionsSet().has_object_permission(request, self, original_post):
            return Response({'detail': 'You do not have permissions to repost this content. Must be: follower, owner, admin/moder.'}, status=status.HTTP_403_FORBIDDEN)
        
        reposted_post = Post.objects.create(
        page=current_page,
        content=original_post.content,
        file=original_post.file,
        reply_to=original_post,
        )

        return Response({'detail': 'Reposted successfully.'}, status=status.HTTP_201_CREATED)

    # Та же история, что и с запросами на подписку. Не нравиться мне. Но чет не доходит, как сделать нормально.
    # Пока что вот так деревянно.
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))

        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        if post.dislikes.filter(author=current_page).first():
            post.dislikes.filter(author=current_page).delete()
            post.likes.create(author=current_page)
            return Response({"message": "Dislike removed, Like added"}, status=201)
        if post.likes.filter(author=current_page).exists():
            post.likes.filter(author=current_page).delete()
            return Response({"message": "Like removed"}, status=200)
        else:
            post.likes.create(author=current_page)
            return Response({"message": "Like added"}, status=201)
        
    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        current_page = Page.objects.get(pk = request.query_params.get('current_page'))
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        if post.likes.filter(author=current_page).first():
            post.likes.filter(author=current_page).delete()
            post.dislikes.create(author=current_page)
            return Response({"message": " Like removed, Dislike added"}, status=201)
        if post.dislikes.filter(author=current_page).exists():
            post.dislikes.filter(author=current_page).delete()
            return Response({"message": "Dislike removed"}, status=200)
        else:
            post.dislikes.create(author=current_page)
            return Response({"message": "Dislike added"}, status=201)

class FeedView(CheckCurrentPageMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not self.check_current_page(request) == None:
            return self.check_current_page(request)
        
        current_page = Page.objects.get(id=request.query_params.get('current_page'))
        
        followed_pages = current_page.page_follows.all()
        feeds_posts = Post.objects.filter(page__in=followed_pages).order_by('-created_at')

        visible_posts = []
        for post in feeds_posts:
            if post.reply_to is not None:
                original_post = Post.objects.get(id=post.reply_to_id)
                if page_permissions.PostsPermissionsSet().has_object_permission(self.request, self, original_post):
                    visible_posts.append(post)
            else:
                visible_posts.append(post)

        serializer = page_serializer.PostSerializer(visible_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)