from rest_framework.permissions import BasePermission
from useraccountsettings.models import UserAccountSettings

class CanAccessSettings(BasePermission):
    def has_object_permission(self, request, view, obj: UserAccountSettings):
        user = request.user

        if user.is_superuser:
            return True

        if user != obj.user_account:
            return False
        return True

    def has_permission(self, request, view):
        """
        For list actions, we can't check a specific object,
        so return True and filter queryset in view (or override get_queryset)
        """
        return True
