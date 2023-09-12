from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

from account import views

from account.views import BlockUserView

app_name = "account"

urlpatterns = [
    path("", views.UserAPIView.as_view(), name="user-info"),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path("profile/", views.UserProfileAPIView.as_view(), name="user-profile"),

    path("register/", views.UserRegistrationAPIView.as_view(), name="create-user"),
    path("login/", views.UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", views.UserLogoutAPIView.as_view(), name="logout-user"),

    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    path("users/<str:username>/block/", BlockUserView.as_view({'post': 'block_user_action'}), name="block_user"),
    path("users/<str:username>/unblock/", BlockUserView.as_view({'post': 'unblock_user_action'}), name="unblock_user"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)