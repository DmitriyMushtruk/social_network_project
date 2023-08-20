from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import TagListViewSet, UserPageListViewSet, PageViewSet

app_name = "page"

router = DefaultRouter()
router.register(r'posts', PageViewSet, basename='pages-posts')

router.register(r"tags", TagListViewSet)
router.register(r"userpagelist", UserPageListViewSet, basename='userpagelist')
router.register(r'pages', PageViewSet, basename='pages')


urlpatterns = [
    path("", include(router.urls)),
    path("pages/<str:name>/posts/<int:pk>/", PageViewSet.as_view({"get": "posts", "post": "posts", "put": "posts", "delete": "posts"}), name="post-detail"),
    path("pages/<str:name>/approve_request/<int:pk>/", PageViewSet.as_view({"post": "approve_request"}), name="page-approve_request"),
 ]

urlpatterns += router.urls