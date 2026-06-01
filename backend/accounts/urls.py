from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Permissions
from .views import UserPermissionsView, UserListView

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/userpermissions/", UserPermissionsView.as_view(), name="userpermissions"),
    path("api/users/", UserListView.as_view(), name="user-list"),
]
