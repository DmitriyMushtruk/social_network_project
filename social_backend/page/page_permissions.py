from rest_framework import permissions
from .models import Page, Post
from account.models import User

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Page):
            return obj.owner == request.user
        if isinstance(obj, Post):
            return obj.page.owner == request.user

class CanViewPage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.is_private:
            current_page = request.query_params.get('current_page')
            if obj.followers.filter(id=current_page).exists():
                return True
            elif obj.owner == request.user:
                return True
            elif user.role == User.Roles.MODERATOR or user.role == User.Roles.ADMIN:
                return True
        else:
            return True

class CanViewPost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.page.is_private:
            current_page = request.query_params.get('current_page')
            if obj.page.followers.filter(id=current_page).exists():
                return True
            elif user == obj.page.owner:
                return True
            elif  user.role == User.Roles.MODERATOR or user.role == User.Roles.ADMIN:
                return True
        else:
            return True