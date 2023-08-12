from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagListViewSet, UserPageListViewSet, PageViewSet

app_name = "posts"

router = DefaultRouter()

router.register(r"tags", TagListViewSet)
router.register(r"user_pagelist", UserPageListViewSet)
router.register(r'page', PageViewSet, basename='page')

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += router.urls