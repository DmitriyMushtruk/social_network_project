from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagListViewSet, UserPageListViewSet, PageViewSet, PostViewSet

app_name = "posts"

router = DefaultRouter()

router.register(r"tags", TagListViewSet)
router.register(r"user_pagelist", UserPageListViewSet)
router.register(r'page', PageViewSet, basename='page')
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += router.urls