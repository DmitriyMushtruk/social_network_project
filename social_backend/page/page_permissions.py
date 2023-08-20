from rest_framework import permissions
from .models import Page

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class CanViewPage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_private:
            current_page = request.query_params.get('current_page')
            return obj.followers.filter(id=current_page).exists()
        elif obj.owner == request.user:
            return True
        else:
            return True
    

    #user_role = request.user.role
        # if request.user.role.MODERATOR or request.user.role.ADMIN:
        #     return True