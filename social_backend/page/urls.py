from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagListViewSet, UserPageListViewSet, PageViewSet, PostViewSet, FeedView

app_name = "page"

router = DefaultRouter()

router.register(r"tags", TagListViewSet)
router.register(r"userpagelist", UserPageListViewSet, basename='userpagelist')
router.register(r'pages', PageViewSet, basename='pages')
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = [
    path("", include(router.urls)),

    path('pages/<str:name>/requests/',
        PageViewSet.as_view({'get': 'get_requests_action'}), name='requests'),
    path(
        'pages/<str:name>/requests/approve/<int:requester_page>/',
        PageViewSet.as_view({'post': 'approve_requests_action'}),
        name='approve_request'
        ),
    path(
        'pages/<str:name>/requests/approve/',
        PageViewSet.as_view({'post': 'approve_requests_action'}),
        kwargs={"requester_page": None}, name='approve_requests'
        ),
    path(
        'pages/<str:name>/requests/reject/<int:requester_page>/',
        PageViewSet.as_view({'post': 'reject_requests_action'}),
        name='reject_request'
        ),
    path(
        'pages/<str:name>/requests/reject/',
        PageViewSet.as_view({'post': 'reject_requests_action'}),
        kwargs={"requester_page": None}, name='reject_requests'
        ),
    path('pages/<str:name>/followers/',
        PageViewSet.as_view({'get': 'get_followers_action'}), name='followers'),
    path('pages/<int:pk>/block/', PageViewSet.as_view({'post': 'block'}), name='block-page'),
    path('pages/<int:pk>/unblock/', PageViewSet.as_view({'post': 'unblock'}), name='unblock-page'),

    path('posts/list/<str:name>/', PostViewSet.as_view({'get': 'get_page_posts_action'}), name='posts_list'),
    path('posts/<int:pk>/like/', PostViewSet.as_view({'post': 'like_action'}), name='like_post'),
    path('posts/<int:pk>/dislike/', PostViewSet.as_view({'post': 'dislike_action'}), name='dislike_post'),
    path('posts/<int:pk>/comment/', PostViewSet.as_view({'post': 'comment_action'}), name='comment_post'),
    path('posts/<int:pk>/repost/', PostViewSet.as_view({'post': 'repost_action'}), name='repost_post'),

    path('feeds/', FeedView.as_view({'get': 'list'}), name='feeds'),
 ]

urlpatterns += router.urls