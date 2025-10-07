from django.db.models import Q
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from .exceptions import OnlyGetMethodAllowed
from rest_framework.exceptions import PermissionDenied
from useraccountsubscription.models import Subscription
from plan.models import Plan
from .permissions import IsAdmin
from useraccountsubscription.api.v1.serializers.normaluserserializer.serializers import SubscriptionRetrivalSerializer, PlanSubscriberRetrivalSerializer
from useraccountsubscription.api.v1.serializers.superuserserializer.serializers import SubscriptionCreateUpdateSerializer as SuperuserSubscriptionCreateUpdateSerializer



class SubscriptionViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    lookup_url_kwarg = "pk"
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "payment_status",
        "user_account__username",
        "is_subscription_active"
    ]
    filterset_fields = [
        "payment_status",
        "user_account__username",
        "is_subscription_active"
    ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            qs = Subscription.objects.all()
        else:
            qs = Subscription.objects.filter(Q(user_account=user))
        return qs

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            if self.request.method == "POST":
                return SuperuserSubscriptionCreateUpdateSerializer
            else:
                return SubscriptionRetrivalSerializer
        else:
            if self.request.method == "GET":
                return SubscriptionRetrivalSerializer
            else:
                raise OnlyGetMethodAllowed

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        return super().get_permissions()



class PlanSubscriberAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlanSubscriberRetrivalSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "user_account__username",
        "is_subscription_active"
    ]
    filterset_fields = [
        "user_account__username",
        "is_subscription_active"
    ]
    

    def get_queryset(self):
        plan_id = self.kwargs.get("pk", None)
        plan = get_object_or_404(Plan, id=plan_id)
        if self.request.user.is_superuser or plan.user_account == self.request.user:
            return Subscription.objects.filter(plan=plan)
        else:
            raise PermissionDenied({"detail": "You don't have access to this data."})

