from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from rest_framework.decorators import action
# from .permissions import CanViewPrivatePage # Пока что не используеться тк, нету возможности протестировать


from .models import Page, Tag, Post, Comment, Like, Dislike
from .serializers import page_serializer

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
        #Return only pages owned by the current user
        return Page.objects.filter(owner=self.request.user)
    
class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    #serializer_class = get_serializer_class(self)
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "name"

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return page_serializer.CreateOrUpdatePageSerializer
        else:
            return page_serializer.PageSerializer
    
    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('name')
        page = Page.objects.filter(name=name).first()

        if page:
            posts = page.posts.all()
            post_serializer = page_serializer.CreateOrUpdatePostSerializer(posts, many=True)
            serializer = self.get_serializer(page)
            data = serializer.data
            data['posts'] = post_serializer.data
            return Response(data)
        else:
            return Response({'detail': 'Page not found.'}, status=404)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Checking if the current user is the owner of the page
        if instance.owner != request.user:
            return Response({'detail': 'You do not have permission to edit this page.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.owner != request.user:
            return Response({'detail': 'You do not have permission to delete this page.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
            instance.delete()

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = page_serializer.CreateOrUpdatePostSerializer

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()  # Получаем объект поста по идентификатору из URL
        serializer = self.get_serializer(post)
        
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        selected_page = 1 # Времанная переменная
        print("selected page id is: ", selected_page) #Test
        print("request user is: ", request.user) #Test

        # Тут должна быть логика для вычисления выбранной пользователем страницы (храним в session)
        #selected_page = request.session.get('selected_page')

        try:
            selected_page = Page.objects.get(id=selected_page)
            print("page owner is: ", selected_page.owner) #Test
        except Page.DoesNotExist:
            return Response({'error': 'Selected page not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if selected_page.owner != request.user:
            print(selected_page.owner, request.user)
            return Response({'detail': 'You do not have permission to created post on this page.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(page=selected_page)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        selected_page = 1 # Времанная переменная

        # Тут должна быть логика для вычисления выбранной пользователем страницы (храним в session)
        #selected_page = request.session.get('selected_page')

        post = self.get_object()  # Получаем объект поста по идентификатору из URL

        try:
            selected_page = Page.objects.get(id=selected_page)
            print("page owner is: ", selected_page.owner) #Test
        except Page.DoesNotExist:
            return Response({'error': 'Selected page not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if selected_page.owner != request.user:
            return Response({'detail': 'You do not have permission to edit this post.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        selected_page = 1 # Времанная переменная

        # Тут должна быть логика для вычисления выбранной пользователем страницы (храним в session)
        #selected_page = request.session.get('selected_page')

        post = self.get_object()

        try:
            selected_page = Page.objects.get(id=selected_page)
            print("page owner is: ", selected_page.owner) #Test
        except Page.DoesNotExist:
            return Response({'error': 'Selected page not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if post.page.owner != request.user:
            print("page owner is: ", post.page.owner )
            return Response({'detail': 'You do not have permission to delete this post.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(post)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        selected_page = 1 # Времанная переменная
        user_page = Page.objects.get(id=selected_page)  # Получаем страницу по временному идентификатору
        post = self.get_object()
        #user_page = request.user.page 

        # Проверяем, есть ли уже отметка дизлайк от этого пользователя
        existing_dislike = post.dislikes.filter(author=user_page).first()

        if existing_dislike:
            existing_dislike.delete()
            post.likes.create(author=user_page)
            return Response({"message": "Dislike removed, Like added"}, status=201)
        if post.likes.filter(author=user_page).exists():
            post.likes.filter(author=user_page).delete()
            return Response({"message": "Like removed"}, status=200)
        else:
            post.likes.create(author=user_page)
            return Response({"message": "Like added"}, status=201)

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        selected_page = 1 # Времанная переменная
        user_page = Page.objects.get(id=selected_page)  # Получаем страницу по временному идентификатору
        post = self.get_object()
        #user_page = request.user.page

        # Проверяем, есть ли уже отметка лайк от этого пользователя
        existing_like = post.likes.filter(author=user_page).first()

        if existing_like:
            existing_like.delete()
            post.dislikes.create(author=user_page)
            return Response({"message": "Like removed, Dislike added"}, status=201)
        if post.dislikes.filter(author=user_page).exists():
            post.dislikes.filter(author=user_page).delete()
            return Response({"message": "Dislike removed"}, status=200)
        else:
            post.dislikes.create(author=user_page)
            return Response({"message": "Dislike added"}, status=201)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        selected_page = 1  # Временная переменная
        user_page = Page.objects.get(id=selected_page)  # Получаем страницу по временному идентификатору
        post = self.get_object()

        comment_text = request.data.get('content')  # Получаем текст комментария из запроса

        # Создаем комментарий
        comment = Comment.objects.create(post=post, author=user_page, content=comment_text)
        serializer = page_serializer.CommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)