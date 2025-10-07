from rest_framework import serializers
from useraccount.api.v1.serializers.generalserializer.serializers import ExternalUserAccountRetrivalSerializer
from plan.models import Plan

class PlanCreationUpdateSerializer(serializers.ModelSerializer):
    effective_price = serializers.SerializerMethodField()
    subscribers_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    def get_effective_price(self, obj):
        return obj.effective_price

    def get_subscribers_count(self, obj):
        return obj.subscribers_count

    def get_posts_count(self, obj):
        return obj.posts_count

    class Meta:
        model = Plan
        fields = "__all__"



class PlanRetrivalSerializer(serializers.ModelSerializer):
    user_account = ExternalUserAccountRetrivalSerializer(read_only=True)
    effective_price = serializers.SerializerMethodField()
    subscribers_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    def get_effective_price(self, obj):
        return obj.effective_price

    def get_subscribers_count(self, obj):
        return obj.subscribers_count

    def get_posts_count(self, obj):
        return obj.posts_count

    class Meta:
        model = Plan
        fields = "__all__"
