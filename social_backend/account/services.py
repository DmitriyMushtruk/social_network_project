from .models import User
from page.models import Page
from rest_framework.response import Response
from datetime import datetime, timedelta

from rest_framework.status import (
    HTTP_200_OK,
)


def block_user(user: User) -> Response:
    user.is_blocked = True
    user.save()
    return Response({'detail': 'User blocked successfully.'}, status=HTTP_200_OK)


def unblock_user(user: User) -> Response:
    user.is_blocked = False
    user.save()
    return Response({'detail': 'User unblocked successfully.'}, status=HTTP_200_OK)
