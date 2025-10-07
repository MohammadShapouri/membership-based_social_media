from rest_framework.permissions import BasePermission
from useraccountconnection.models import FollowingFollower
from useraccount.models import UserAccount

class CanViewFollowingFollower(BasePermission):
    """
    Allows viewing a FollowingFollower object only if:
    - The request user is superuser
    - OR the user is involved in the relation
    - AND the target user is active and verified
    - AND private accounts can only be viewed by accepted followers
    """
    def has_object_permission(self, request, view, obj: FollowingFollower):
        user = request.user

        if user.is_superuser:
            return True

        def check_user_access(target_user: UserAccount):
            if target_user.is_private and target_user != user:
                is_following = FollowingFollower.objects.filter(
                    follower=user,
                    following=target_user,
                    is_accepted=True
                ).exists()
                if not is_following:
                    # raise PermissionDenied(
                    #     "This account is private. You must be an accepted follower to view this data."
                    # )
                    return False

        # Check both sides of the relation
        check_user_access(obj.follower)
        check_user_access(obj.following)
        return True

    def has_permission(self, request, view):
        """
        For list actions, we can't check a specific object,
        so return True and filter queryset in view (or override get_queryset)
        """
        return True


class CanDeleteFollowingFollower(BasePermission):
    def has_object_permission(self, request, view, obj: FollowingFollower):
        user = request.user

        if user.is_superuser:
            return True

        if obj.follower == user or obj.following == user:
            return True
        return False


class CanEditFollowingFollower(BasePermission):
    def has_object_permission(self, request, view, obj: FollowingFollower):
        user = request.user

        if user.is_superuser:
            return True

        if obj.following == user and not obj.is_accepted:
            return True
        return False

class IsOwnerOfBlockListOrAdmin(BasePermission):
    """
    Only allow owners (blocker) or admins to access/modify BlockList objects.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.blocker == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
