from rest_framework import serializers
from useraccountconnection.models import FollowingFollower, BlockList
from useraccount.api.v1.serializers.generalserializer.serializers import ExternalUserAccountRetrivalSerializer


class FollowerFollowingCreationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowingFollower
        fields = "__all__"

    def validate(self, attrs):
        """
        Check if a relation between follower and following already exists.
        """
        follower = attrs.get('follower')
        following = attrs.get('following')

        if follower and following:
            qs = FollowingFollower.objects.filter(
                follower=follower,
                following=following
            )

            # exclude self if updating
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError({"detail": "A following relationship between this follower and following already exists."})

        if following == follower:
            raise serializers.ValidationError({"detail": "A following relationship between same user can not exist."})
        return attrs



class FollowerFollowingRetrivalSerializer(serializers.ModelSerializer):
    follower = ExternalUserAccountRetrivalSerializer(read_only=True)
    following = ExternalUserAccountRetrivalSerializer(read_only=True)

    class Meta:
        model = FollowingFollower
        fields = "__all__"




# class BlockListCreationUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BlockList
#         fields = "__all__"


#     def validate(self, attrs):
#         """
#         Check if a relation between blocker and blocked already exists.
#         """
#         blocker = attrs.get('blocker')
#         blocked = attrs.get('blocked')

#         if blocked:
#             qs = BlockList.objects.filter(
#                 blocker=blocker,
#                 blocked=blocked
#             )

#             if self.instance:
#                 qs = qs.exclude(pk=self.instance.pk)

#             if qs.exists():
#                 raise serializers.ValidationError({"detail": "A blocking relationship between this blocker and blocked user already exists."})
            
#         if blocked == blocker:
#             raise serializers.ValidationError({"detail": "A blocking relationship between same user can not exist."})
#         return super().validate(attrs)
    


class BlockListCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockList
        fields = "__all__"


    def validate(self, attrs):
        """
        Check if a relation between blocker and blocked already exists.
        """
        blocker = attrs.get('blocker')
        blocked = attrs.get('blocked')

        if blocked:
            qs = BlockList.objects.filter(
                blocker=blocker,
                blocked=blocked
            )

            if qs.exists():
                raise serializers.ValidationError({"detail": "A blocking relationship between this blocker and blocked user already exists."})
            
        if blocked == blocker:
            raise serializers.ValidationError({"detail": "A blocking relationship between same user can not exist."})
        return super().validate(attrs)
    




class BlockListRetrivalSerializer(serializers.ModelSerializer):
    blocker = ExternalUserAccountRetrivalSerializer(read_only=True)
    blocked = ExternalUserAccountRetrivalSerializer(read_only=True)

    class Meta:
        model = BlockList
        fields = "__all__"
