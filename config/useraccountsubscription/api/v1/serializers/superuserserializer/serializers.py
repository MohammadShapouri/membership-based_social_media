from rest_framework import serializers
from useraccountsubscription.models import Subscription



class SubscriptionCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = "__all__"
