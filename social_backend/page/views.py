from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
# from .permissions import CanViewPrivatePage # Пока что не используеться тк, нету возможности протестировать


from .models import Page, Tag
from .serializers import page_serializer

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
    serializer_class = page_serializer.CreateOrUpdatePageSerializer
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
    
    def perform_destroy(self, instance):
        if instance.owner == self.request.user:
            instance.delete()
        else:
            return Response({"error": "You are not the owner of this page."},
                            status=status.HTTP_403_FORBIDDEN)