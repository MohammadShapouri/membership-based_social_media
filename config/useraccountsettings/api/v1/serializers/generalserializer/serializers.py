from rest_framework import serializers
from useraccountsettings.models import UserAccountSettings
from useraccount.api.v1.serializers.generalserializer.serializers import ExternalUserAccountRetrivalSerializer



class UserAccountSettingsSerializer(serializers.ModelSerializer):
    user_account = ExternalUserAccountRetrivalSerializer(read_only=True)

    class Meta:
        model = UserAccountSettings
        exclude = ["creation_date"]
