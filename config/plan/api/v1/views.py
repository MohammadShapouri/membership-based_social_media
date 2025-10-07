from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .permissions import CanManagePlan
from plan.models import Plan
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from useraccountconnection.models import FollowingFollower, BlockList
from .serializers.normaluserserializers.serializers import PlanCreationSerializer, PlanUpdateRetrivalSerializer
from .serializers.superuserserializers.serializers import (
                                                            PlanCreationUpdateSerializer as SuperuserPlanCreationUpdateSerializer,
                                                            PlanRetrivalSerializer as SuperuserPlanRetrivalSerializer
                                                            )



class PlanModelViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'user_account',
        'user_account__username',
    ]

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
            qs = Plan.objects.all()
        else:
            qs = Plan.objects.filter(
                Q(user_account__in=following_ids) |
                ~Q(user_account__in=blocked_current_user_ids) |
                Q(user_account__is_private=False) |
                Q(user_account=current_user)
            ).distinct()

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, CanManagePlan]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, CanManagePlan]
        elif self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, CanManagePlan]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            if self.request.method in ['POST', 'PUT', 'PATCH']:
                return SuperuserPlanCreationUpdateSerializer
            else:
                return SuperuserPlanRetrivalSerializer
        else:
            if self.request.method == 'POST':
                return PlanCreationSerializer
            else:
                return PlanUpdateRetrivalSerializer
