from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from django.shortcuts import get_object_or_404

from .models import User, Profile
from .permissions import IsAdmin

from .serializers.user_serializer import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    ProfileSerializer,
)

from rest_framework.mixins import (
    UpdateModelMixin,
)

from .services import (
    block_user,
    unblock_user,
)


class UserRegistrationAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)


class UserLogoutAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserLogoutSerializer

    # serializer_class = user_serializer.UserLoginSerializer
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserProfileAPIView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BlockUserView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=['post'],
    )
    def block_user_action(self, request, username=None):
        """This action allows users to follow or unfollow pages"""
        request.data['username'] = username
        user = get_object_or_404(User, username=username)
        return block_user(user)

    @action(
        detail=True,
        methods=['post'],
    )
    def unblock_user_action(self, request, username=None):
        """This action allows users to follow or unfollow pages"""
        request.data['username'] = username
        user = get_object_or_404(User, username=username)
        return unblock_user(user)
