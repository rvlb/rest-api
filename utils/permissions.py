from django.contrib.auth import get_user_model

from rest_framework import permissions

User = get_user_model()

class IsAdminOrSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or self.is_self(request, view))

    def is_self(self, request, view):
        try:
            requested_user = User.objects.get(pk=view.kwargs.get('pk'))
            return request.user.id is requested_user.id
        except User.DoesNotExist:
            return False