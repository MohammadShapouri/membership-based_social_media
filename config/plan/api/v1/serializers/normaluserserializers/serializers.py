from rest_framework import serializers
from useraccount.api.v1.serializers.generalserializer.serializers import ExternalUserAccountRetrivalSerializer
from plan.models import Plan

class PlanCreationSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get("user", None)
        self.fields['user_account'].read_only = True
        self.fields['user_account'].required = False
        self.fields['creation_date'].read_only = True
        self.fields['creation_date'].required = False
    
    effective_price = serializers.SerializerMethodField()

    def get_effective_price(self, obj):
        return obj.effective_price

    class Meta:
        model = Plan
        exclude = ['update_date']

    def save(self, **kwargs):
        self.validated_data['user_account'] = self.user
        return super().save(**kwargs)



class PlanUpdateRetrivalSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_account'] = ExternalUserAccountRetrivalSerializer(read_only=True)
        self.fields['creation_date'].read_only = True
        self.fields['creation_date'].required = False
    
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
        exclude = ['update_date']
