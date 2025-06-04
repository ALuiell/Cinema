from rest_framework import permissions

class IsManager(permissions.BasePermission):
    message = "Need role manager"

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Manager').exists()
        )
