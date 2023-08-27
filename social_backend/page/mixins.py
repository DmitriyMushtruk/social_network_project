from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Page
from .page_permissions import IsOwner

class CheckCurrentPageMixin(APIView):
    def check_current_page(self, request):
        current_page_id = request.query_params.get('current_page')

        try:
            current_page = Page.objects.get(id=current_page_id)
        except Page.DoesNotExist:
            return Response({"detail": "Page not found - 'current_page' is incorrect. "}, status=status.HTTP_404_NOT_FOUND)
        
        if not IsOwner().has_object_permission(request, self, current_page):
            return Response({'detail': 'You are not the owner of this page.'}, status=status.HTTP_403_FORBIDDEN)
        
        return None