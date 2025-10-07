from django.db.models import Q
from useraccount.models import UserAccount
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from useraccountconnection.models import FollowingFollower, BlockList
from rest_framework.views import APIView
from .permissions import CanDeleteFollowingFollower, CanViewFollowingFollower, CanEditFollowingFollower, IsOwnerOfBlockListOrAdmin
from rest_framework.exceptions import PermissionDenied
from useraccountconnection.api.v1.serializers.normaluserserializer.serializers import (
                                                                    FollowerFollowingCreationSerializer,
                                                                    BlockListCreationSerializer,
                                                                    FollowerFollowingRetrivalUpdateSerializer,
                                                                    BlockListRetrivalSerializer,
                                                                    )
from useraccountconnection.api.v1.serializers.superuserserializer.serializers import (
                                                                    FollowerFollowingCreationUpdateSerializer as SuperuserFollowerFollowingCreationUpdateSerializer,
                                                                    BlockListCreationSerializer as SuperuserBlockListCreationSerializer,
                                                                    FollowerFollowingRetrivalSerializer as SuperuserFollowerFollowingRetrivalSerializer,
                                                                    BlockListRetrivalSerializer as SuperuserBlockListRetrivalSerializer
                                                                    )



class FollowerFollowingViewSet(ModelViewSet):
    queryset = UserAccount.objects.all()
    lookup_url_kwarg = 'pk'
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'follower__username',
        'follower__full_name',
        'following__username',
        'following__full_name',
    ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def _check_user_access(self, request_user, target_user: UserAccount):
        """Check if request_user has permission to view target_user."""
        # # Must be active & verified
        # if not (target_user.is_active and target_user.is_account_verified):
        #     raise PermissionDenied("Target user is inactive or not verified.")

        # Private account rule
        if target_user.is_private and target_user != request_user:
            is_following = FollowingFollower.objects.filter(
                follower=request_user,
                following=target_user,
                is_accepted=True,
            ).exists()
            if not is_following:
                raise PermissionDenied(
                    "This account is private. You must be an accepted follower to view this data."
                )

    def get_queryset(self):
        user = self.request.user

        # Base queryset
        if user.is_superuser:
            qs = FollowingFollower.objects.all()
        else:
            qs = FollowingFollower.objects.filter(
                Q(follower__is_active=True, follower__is_account_verified=True)
                & Q(following__is_active=True, following__is_account_verified=True)
            )

        follower_id = self.request.query_params.get("follower")
        following_id = self.request.query_params.get("following")
        target_user_id = follower_id or following_id

        if not user.is_superuser and target_user_id:
            target_user = get_object_or_404(UserAccount, pk=target_user_id)
            self._check_user_access(user, target_user)

            if target_user != user:
                qs.filter(is_accepted=True)

            if following_id:
                qs = qs.filter(Q(follower=following_id))
            elif follower_id:
                qs = qs.filter(Q(following=follower_id))
        return qs

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            if self.request.method == 'POST':
                return SuperuserFollowerFollowingCreationUpdateSerializer
            else:
                return SuperuserFollowerFollowingRetrivalSerializer
        else:
            if self.request.method == 'POST':
                return FollowerFollowingCreationSerializer
            else:
                return FollowerFollowingRetrivalUpdateSerializer  

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, CanEditFollowingFollower]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, CanDeleteFollowingFollower]
        elif self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, CanViewFollowingFollower]
        return super().get_permissions()





class BlockListViewSet(ModelViewSet):
    queryset = UserAccount.objects.all()
    lookup_url_kwarg = 'pk'
    filter_backends = [filters.SearchFilter]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    search_fields = [
        'blocker__username',
        'blocker__full_name',
        'blocked__username',
        'blocked__full_name',
    ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_queryset(self):
        user = self.request.user
        # Base queryset
        if user.is_superuser:
            qs = BlockList.objects.all()
        else:
            qs = BlockList.objects.filter(
                Q(blocker=user)
                & Q(blocked__is_active=True, blocked__is_account_verified=True)
            )
        return qs

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            if self.request.method == 'POST':
                return SuperuserBlockListCreationSerializer
            else:
                return SuperuserBlockListRetrivalSerializer
        else:
            if self.request.method == 'POST':
                return BlockListCreationSerializer
            else:
                return BlockListRetrivalSerializer  

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwnerOfBlockListOrAdmin]
        elif self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsOwnerOfBlockListOrAdmin]
        else:
            self.permission_classes = [IsAuthenticated, IsOwnerOfBlockListOrAdmin]
        return super().get_permissions()

    def perform_create(self, serializer: BlockListCreationSerializer):
        blocked = serializer.validated_data.get("blocked")
        if not isinstance(blocked, UserAccount):
            blocked = UserAccount.objects.get(pk=blocked)

        obj = FollowingFollower.objects.filter(
                follower=self.request.user,
                following=blocked,
            )
        if obj.exists():
            obj.delete()

        obj = FollowingFollower.objects.filter(
                following=self.request.user,
                follower=blocked,
            )
        if obj.exists():
            obj.delete()
        return super().perform_create(serializer)



class UserFollowStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Returns the number of followers and followings for the given pk.
        Respects private accounts: only accepted followers can see stats of private accounts.
        """
        user = get_object_or_404(UserAccount, pk=pk)

        num_follower = FollowingFollower.objects.filter(
            following=user,
            follower__is_active=True,
            follower__is_account_verified=True,
            is_accepted=True
        ).count()

        num_following = FollowingFollower.objects.filter(
            follower=user,
            following__is_active=True,
            following__is_account_verified=True,
            is_accepted=True
        ).count()

        return Response({
            "user_id": user.id,
            "username": user.username,
            "num_follower": num_follower,
            "num_following": num_following
        })





class CurrentUserFollowingStatsAPIView(APIView):
    """
    true means that current user follows user with id given in the url.
    false means that current user does not follow user with id given in the url.
    null means pending.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(UserAccount, pk=pk)

        qs = FollowingFollower.objects.filter(
            follower=request.user,
            following=user
        )
        does_follow = False

        if qs.count() > 0:
            qs = qs.first()
            if qs.is_accepted:
                does_follow = True
            else:
                does_follow = None
            return Response({
                "follows": does_follow,
                "connection_id": qs.id
            })
        else:
            return Response({
                "follows": does_follow,
                "connection_id": None
            })





class CurrentUserBlockStatsAPIView(APIView):
    """
    true means that current user follows user with id given in the url.
    false means that current user does not follow user with id given in the url.
    null means pending.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(UserAccount, pk=pk)

        qs = BlockList.objects.filter(
            blocker=request.user,
            blocked=user
        )

        if qs.exists():
            return Response({
                "blocked": True,
                "block_id": qs.first().id
            })
        else:
            return Response({
                "blocked": False,
                "block_id": None
            })
