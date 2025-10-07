from rest_framework.permissions import BasePermission
from plan.models import Plan

class CanManagePlan(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj: Plan):
        if request.user.is_superuser:
            return True
        if obj.user_account == request.user:
            return True
        return False
