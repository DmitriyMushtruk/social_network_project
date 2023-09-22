from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

from account import views

from account.views import BlockUserView

app_name = "account"

urlpatterns = [
    path("", views.UserAPIView.as_view(), name="user-info"),

    path("api/register/", views.UserRegistrationAPIView.as_view(), name="create-user"),
    path("api/login/", views.UserLoginAPIView.as_view(), name="login-user"),
    path("api/logout/", views.UserLogoutAPIView.as_view(), name="logout-user"),

    path('api/users/', views.UserListView.as_view(), name='user-list'),
    path('api/users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('api/users/me/', views.UserAPIView.as_view(), name='user-me'),
    path("api/profile/", views.UserProfileAPIView.as_view(), name="user-profile"),


    path("api/users/<uuid:pk>/block/", BlockUserView.as_view({'put': 'block_user_action'}), name="block_user"),
    path("api/users/<uuid:pk>/unblock/", BlockUserView.as_view({'put': 'unblock_user_action'}), name="unblock_user"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)