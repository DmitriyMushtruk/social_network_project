from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import TagListViewSet, UserPageListViewSet, PageViewSet, PostViewSet

app_name = "page"

router = DefaultRouter()


router.register(r"tags", TagListViewSet)
router.register(r"userpagelist", UserPageListViewSet, basename='userpagelist')
router.register(r'pages', PageViewSet, basename='pages')
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = [
    path("", include(router.urls)),
    path('pages/<str:name>/requests/approve/<int:id_page>/', PageViewSet.as_view({'post': 'approve_request'}), name='approve-request'),
    path('pages/<str:name>/requests/reject/<int:id_page>/', PageViewSet.as_view({'post': 'reject_request'}), name='reject-request'),
 ]

urlpatterns += router.urls