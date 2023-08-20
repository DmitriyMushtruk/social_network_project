from rest_framework import permissions, status, viewsets, mixins
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from rest_framework.decorators import action
from rest_framework import status

from .models import Page, Tag, Post, Comment, Like, Dislike
from .serializers import page_serializer
from . import page_permissions

def select_page(request, page_id):
    selected_page = Page.objects.get(id=page_id)
    if selected_page.owner != request.user:
        return HttpResponseForbidden("You are not the owner of this page.")
    
    request.session['selected_page'] = page_id
    
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
    
    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

# Сделать проверку что пользователь подписан на страницу (если она приватная), если он пытаеться просмотреть страницы и ее посты 
class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = page_serializer.PageSerializer
    lookup_field = "name"

    def get_queryset(self):
        name = self.kwargs.get('name')
        print("kwargs id", self.kwargs.get("name"))
        return Page.objects.prefetch_related('posts').filter(name=name).first()
    
    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [page_permissions.IsOwner()]
        return super().get_permissions()
        
    def retrieve(self, request, *args, **kwargs):
        page = self.get_queryset()

        if not page_permissions.CanViewPage().has_object_permission(request, self, page):
            return Response({'detail': 'You are not follower of this PRIVATE page.'}, status=status.HTTP_403_FORBIDDEN)
        
        if page:
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        else:
            return Response({'detail': 'Page not found.'}, status=404)
        

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
        # serializer = self.get_serializer(page, data=request.data, partial=True) проверить хэндлиться ли все остальное через модел вью сет
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(page, '_prefetched_objects_cache', None):
            page._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        page = self.get_queryset()
        self.perform_destroy(page)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['get', 'post', 'put', 'delete'])
    def posts(self, request, name=None, pk=None):
        page = self.get_queryset()

        if not page_permissions.CanViewPage().has_object_permission(request, self, page):
            return Response({'detail': 'You are not follower of this PRIVATE page.'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == "GET":
            if page:
                if pk is not None:
                    post = Post.objects.filter(page=page, pk=pk).first()
                    print("POST IS: ", post)
                    if not post:
                        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        
                    serializer = page_serializer.PostSerializer(post)
                    return Response(serializer.data)
                else:
                    posts = page.posts.all()
                    serializer = page_serializer.PostSerializer(posts, many=True)
                    return Response(serializer.data)
            else:
                return Response({'detail': 'Page not found.'}, status=404)

        elif request.method == 'POST':
            if not page_permissions.IsOwner().has_object_permission(request, self, page):
                return Response({'detail': 'You are not the owner of this page.'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = page_serializer.PostSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(page=page)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        elif request.method == 'PUT' or request.method == 'DELETE':
            if not page_permissions.IsOwner().has_object_permission(request, self, page):
                return Response({'detail': 'You are not the owner of this page.'}, status=status.HTTP_403_FORBIDDEN)
            
            post = Post.objects.filter(page=page, pk=pk).first()
            if not post:
                return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            if request.method == 'PUT':
                serializer = page_serializer.PostSerializer(post, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            elif request.method == 'DELETE':
                post.delete()
                return Response({'detail': 'Post has been deleted.'},status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                
    @action(detail=True, methods=['post'])
    def follow(self, request, name=None):
        page = self.get_queryset()
        current_page = request.query_params.get('current_page')

        if page.is_private:
            page.follow_requests.add(current_page)  # Добавляем в список ожидающих
            return Response({'detail': 'Follow request sent successfully.'}, status=status.HTTP_200_OK)

        page.followers.add(current_page)  # Просто добавляем в подписчики
        return Response({'detail': 'Followed successfully.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, name=None):
        page = self.get_queryset()
        current_page = request.query_params.get('current_page')

        page.followers.remove(current_page)
        return Response({'detail': 'Unfollowed successfully.'}, status=status.HTTP_200_OK)


    # Доделать возможность принимать запросы и отклонять. Протестировать
    @action(detail=True, methods=['post'])
    def approve_request(self, request, name=None, pk=None):
        page = self.get_object()

        if not page_permissions.IsOwner().has_object_permission(request, self, page):
            return Response({'detail': 'You are not the owner of this page.'}, status=status.HTTP_403_FORBIDDEN)

        if page:
            requester_page = page.follow_requests.filter(page=page, pk=pk).first()
            if requester_page:
                page.followers.add(requester_page)  # Добавляем в подписчики
                page.follow_requests.remove(requester_page)  # Убираем из списка ожидающих
                return Response({'detail': 'Request approved successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'Page not found.'}, status=404)

    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        page = self.get_object()

        if page.owner != request.user:
            return Response({'detail': 'You do not have permission to reject requests.'}, status=status.HTTP_403_FORBIDDEN)

        requester_page = page.follow_requests.filter(requester=request.user.page).first()
        if requester_page:
            page.follow_requests.remove(requester_page)  # Убираем из списка ожидающих
            return Response({'detail': 'Request rejected successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)
    

    # Нужны ли делать проверку request.user == isAuntheficated? или лучше сделать в начале PageViewSet?
    
    @action(detail=True, methods=['post'])
    def comment(self, request, name=None, pk=None):
        page = self.get_queryset()
        if page:
            post = Post.objects.filter(page=page, pk=pk).first()
            if not post:
                return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            comment_text = request.data.get('content')
            user_page = Page.objects.get(id=request.user.current_page)

            comment = Comment.objects.create(post=post, author=user_page, content=comment_text)
            serializer = page_serializer.CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Page not found.'}, status=status.HTTP_404_NOT_FOUND)