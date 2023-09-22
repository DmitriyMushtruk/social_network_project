from .models import User
from rest_framework import permissions


class IsNotAuthenticated(permissions.BasePermission):
    """Checks if user is authenticated"""
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """The request is authenticated as a user, or is a read-only request."""
    def has_permission(self, request, view):
        return bool(
            request.method in ('GET', 'HEAD', 'OPTIONS') or
            request.user and
            request.user.is_authenticated
        )


class IsAdmin(permissions.BasePermission):
    """ Checks if the user have an admin role """

    def has_permission(self, request, view):
        user = request.user
        return user.role == User.Roles.ADMIN
