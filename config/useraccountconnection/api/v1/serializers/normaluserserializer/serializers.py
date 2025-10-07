from rest_framework import serializers
from useraccountconnection.models import FollowingFollower, BlockList
from useraccount.api.v1.serializers.generalserializer.serializers import ExternalUserAccountRetrivalSerializer
from useraccount.models import UserAccount
from django.utils import timezone

class FollowerFollowingCreationSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        self.user = self.context.get("user", None)
        self.fields['follower'].read_only = True
        self.fields['follower'].required = True
        self.fields['is_accepted'].read_only = True

    class Meta:
        model = FollowingFollower
        exclude = ['acception_date', 'creation_date']

    def validate(self, attrs):
        """
        Check if a relation between follower and following already exists.
        """
        following = attrs.get('following')

        if following:
            exists = FollowingFollower.objects.filter(
                follower=self.user,
                following=following
            ).exists()

            if exists:
                raise serializers.ValidationError({"detail": "A following relationship between this follower and following already exists."})
            
        if following == self.user:
            raise serializers.ValidationError({"detail": "A following relationship between same user can not exist."})
        return super().validate(attrs)
    

    def save(self, **kwargs):
        following = self.validated_data.get("following")
        if not isinstance(following, UserAccount):
            following = UserAccount.objects.get(pk=following)

        if following.is_private:
            self.validated_data['is_accepted'] = False
        else:
            self.validated_data['is_accepted'] = True
        self.validated_data['follower'] = self.user
        return super().save(**kwargs)




class FollowerFollowingRetrivalUpdateSerializer(serializers.ModelSerializer):
    follower = ExternalUserAccountRetrivalSerializer(read_only=True)
    following = ExternalUserAccountRetrivalSerializer(read_only=True)

    class Meta:
        model = FollowingFollower
        exclude = ['acception_date', 'creation_date']

    def validate(self, attrs):
        # If updating an existing instance
        instance = getattr(self, 'instance', None)

        # Get the new value (from request) or keep existing
        new_is_accepted = attrs.get("is_accepted")
        
        if instance:
            # Prevent changing is_accepted if it's already True
            if instance.is_accepted and new_is_accepted is True:
                raise serializers.ValidationError({
                    "is_accepted": "You can't change accepted requests' is_accepted field."
                })
        return super().validate(attrs)


    def save(self, **kwargs):
        self.validated_data['acception_date'] = timezone.now()
        return super().save(**kwargs)



class BlockListCreationSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        self.user = self.context.get("user", None)
        self.fields['blocker'].read_only = True
        self.fields['blocker'].required = True
        self.fields['creation_date'].read_only = True
        self.fields['creation_date'].required = True

    class Meta:
        model = BlockList
        fields = "__all__"


    def validate(self, attrs):
        """
        Check if a relation between blocker and blocked already exists.
        """
        blocked = attrs.get('blocked')

        if blocked:
            exists = BlockList.objects.filter(
                blocker=self.user,
                blocked=blocked
            ).exists()

            if exists:
                raise serializers.ValidationError({"detail": "A blocking relationship between this blocker and blocked user already exists."})
            
        if blocked == self.user:
            raise serializers.ValidationError({"detail": "A blocking relationship between same user can not exist."})
        return super().validate(attrs)


    def save(self, **kwargs):
        self.validated_data['blocker'] = self.user
        return super().save(**kwargs)



class BlockListRetrivalSerializer(serializers.ModelSerializer):
    blocker = ExternalUserAccountRetrivalSerializer(read_only=True)
    blocked = ExternalUserAccountRetrivalSerializer(read_only=True)

    class Meta:
        model = BlockList
        fields = "__all__"
