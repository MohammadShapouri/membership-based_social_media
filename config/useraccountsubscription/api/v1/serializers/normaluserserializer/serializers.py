from rest_framework import serializers
from useraccountsubscription.models import Subscription
from useraccount.api.v1.serializers.generalserializer.serializers import ExternalUserAccountRetrivalSerializer
from plan.api.v1.serializers.generalserializers.serializers import ExternalPlanRetrivalSerializer



class SubscriptionRetrivalSerializer(serializers.ModelSerializer):
    user_account = ExternalUserAccountRetrivalSerializer(read_only=True)
    plan = ExternalPlanRetrivalSerializer(read_only=True)
    plan_owner = serializers.SerializerMethodField(read_only=True)

    def get_plan_owner(self, obj):
        if obj.plan:
            return ExternalUserAccountRetrivalSerializer(obj.plan.user_account).data
        else:
            return []

    class Meta:
        model = Subscription
        fields = "__all__"
        extra_fields = ["plan_owner"]





class PlanSubscriberRetrivalSerializer(serializers.ModelSerializer):
    user_account = ExternalUserAccountRetrivalSerializer(read_only=True)

    def get_plan_owner(self, obj):
        if obj.plan:
            return ExternalUserAccountRetrivalSerializer(obj.plan.user_account).data
        else:
            return []

    class Meta:
        model = Subscription
        fields = ["user_account", "is_subscription_active"]
