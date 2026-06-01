from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class UserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_permissions = user.get_all_permissions()
        all_permissions = Permission.objects.filter(
            codename__in=[perm.split(".")[1] for perm in user_permissions]
        ).select_related("content_type")
        grouped_permissions = {}
        for perm in all_permissions:
            model = perm.content_type.model
            if model not in grouped_permissions:
                grouped_permissions[model] = []
            grouped_permissions[model].append(perm.codename)
        return Response(
            {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "permissions_by_model": grouped_permissions,
            }
        )


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        User = get_user_model()
        users = User.objects.filter(is_active=True).order_by("last_name", "first_name")
        return Response(
            [
                {
                    "id": u.id,
                    "username": u.username,
                    "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
                }
                for u in users
            ]
        )
