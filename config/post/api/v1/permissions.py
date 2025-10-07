from rest_framework.permissions import BasePermission


class IsOwnerOfContent(BasePermission):
    def has_object_permission(self, request, view, obj):
        # return obj.user_account == request.user or obj.plan is None or (obj.plan is not None and obj.plan in request.user.subscriptions.all())
        return True
    
    def has_permission(self, request, view):
        return request.user.is_authenticated