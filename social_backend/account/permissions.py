from .models import User
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """ Checks if the user have an admin role """

    def has_permission(self, request, view):
        user = request.user
        return user.role == User.Roles.ADMIN
