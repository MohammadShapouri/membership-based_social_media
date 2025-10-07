from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
        return False