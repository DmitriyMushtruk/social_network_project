from rest_framework import permissions
from .models import Page, Post
from account.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

class IsOwner(permissions.BasePermission):
    """ Checks if the user is the owner of the object """
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Page):
            return obj.owner == request.user
        if isinstance(obj, Post):
            return obj.page.owner == request.user
        
class IsAdminOrModer(permissions.BasePermission):
    """ Checks if the user have a admin or moderator role """

    def has_permission(self, request, view):
        user = request.user
        if user.role == User.Roles.MODERATOR or user.role == User.Roles.ADMIN:
            return True
        else:
            return False
        
class CheckCurrentPage(permissions.BasePermission):
    """
    Checking the user's current page. Checks if the given page exists and if the user owns it
    """
    def has_permission(self, request, view):
        current_page = get_object_or_404(Page.objects.all(), id=request.query_params.get('current_page'))

        if current_page and current_page.owner == request.user:
            return True
        else:
            return False
        
class CheckPageBlockStatus(permissions.BasePermission):
    """
    Checks the block status of the page.
    If the page is blocked access will be denied.
    If the page blocking time has passed - the page will be unblocked and become available.
    Administrators and moderators have access to blocked pages.
    """
    def has_permission(self, request, view):
        user = request.user
        page = view.get_object()
        
        if user.role == User.Roles.MODERATOR or user.role == User.Roles.ADMIN:
            return True
        if page.unblock_date == None:
            return True
        elif page.unblock_date is not None and page.unblock_date <= timezone.now():
            page.unblock_date = None
            page.save()
            return True
        else:
            self.message = {'detail': f"Page is blocked until {page.unblock_date}. Time left: {page.unblock_date - timezone.now()}."}
            return False

class CanViewPage(permissions.BasePermission):
    """ 
    Checking if the user can view the page.
    To gain access to a private page, the user must be: admin/moder, follower. 
    """
    def has_object_permission(self, request, view, obj):
        
        user = request.user
        if obj.is_private:
            current_page = request.query_params.get('current_page')
            if obj.followers.filter(id=current_page).exists() or user.role == User.Roles.MODERATOR or user.role == User.Roles.ADMIN:
                return True
            else:
                return False
        else:
            return True

class CanViewPost(permissions.BasePermission):
    """ 
    Checking if the user can view the post.
    Checks if the post is a repost from another page,
    and checks if the user has access to this page.
    If the post page is private - checks if the user
    has access to this page.
    Also checks if the user is the owner of the post 
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        current_page = request.query_params.get('current_page')

        if obj.reply_to is not None:
            original_post = Post.objects.get(id=obj.reply_to.id)
            if original_post.page.followers.filter(id=current_page).exists():
                return True
            else:
                return False
        elif obj.page.is_private:
            if obj.page.followers.filter(id=current_page).exists():
                return True
            else:
                return False
        elif user == obj.page.owner:
            return True
        else:
            return True