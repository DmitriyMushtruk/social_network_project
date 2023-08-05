from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

from account import views

app_name = "account"

urlpatterns = [
    #path('', views.hello, name='hello'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path("register/", views.UserRegisterationAPIView.as_view(), name="create-user"),
    path("login/", views.UserLoginAPIView.as_view(), name="login-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", views.UserLogoutAPIView.as_view(), name="logout-user"),
    path("", views.UserAPIView.as_view(), name="user-info"),
    path("profile/", views.UserProfileAPIView.as_view(), name="user-profile"),
    path("profile/avatar/", views.UserAvatarAPIView.as_view(), name="user-avatar"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)