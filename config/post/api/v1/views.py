from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from post.models import Post
from django.db.models import Q
from useraccountconnection.models import FollowingFollower, BlockList
from .permissions import IsOwnerOfContent
from django_filters.rest_framework import DjangoFilterBackend
from .serializers.superuserserializers.serializers import (
                                                            PostPostUpdateSerializer as SuperuserPostPostUpdateSerializer,
                                                            PostRetrivalSerializer as SuperuserPostRetrivalSerializer
                                                            )
from .serializers.normaluserserializers.serializers import (
                                                            PostPostUpdateSerializer,
                                                            PostRetrivalSerializer
                                                            )



class PostViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'user_account',
        'user_account__username',
        'plan'
    ]
    permission_classes = [IsAuthenticated, IsOwnerOfContent]

    def get_queryset(self):
        current_user = self.request.user
        qs = None
        following_ids = FollowingFollower.objects.filter(
            follower=current_user, 
            is_accepted=True
        ).values_list('following_id', flat=True)

        # Get IDs of users who blocked me
        blocked_current_user_ids = BlockList.objects.filter(
            blocked=current_user
        ).values_list('blocker_id', flat=True)

        if self.request.user.is_superuser:
            qs = Post.objects.all()
        else:
            qs = Post.objects.filter(
                (Q(user_account__in=following_ids) |
                ~Q(user_account__in=blocked_current_user_ids) |
                Q(user_account__is_private=False) |
                Q(user_account=current_user))
            ).distinct()
        return qs

    def get_serializer_class(self):
        user = self.request.user
        if user.is_superuser:
            if self.request.method in ["POST", "PUT", "PATCH"]:
                return SuperuserPostPostUpdateSerializer
            else:
                return SuperuserPostRetrivalSerializer
        else:
            if self.request.method in ["POST", "PUT", "PATCH"]:
                return PostPostUpdateSerializer
            else:
                return PostRetrivalSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def perform_create(self, serializer):
        # Normal users automatically set themselves as the owner
        if not self.request.user.is_superuser:
            serializer.save(user_account=self.request.user)
        else:
            serializer.save()
