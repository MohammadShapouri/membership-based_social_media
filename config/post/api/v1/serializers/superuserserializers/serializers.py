from rest_framework import serializers
from post.models import Post, PostFileContent
from useraccount.api.v1.serializers.generalserializer.serializers import ExternalUserAccountRetrivalSerializer
from plan.api.v1.serializers.generalserializers.serializers import ExternalPlanRetrivalSerializer
from customserializers.serializers import RelativeFileField, RelativeImageField

class PostFileContentSerializer(serializers.ModelSerializer):
    file = RelativeFileField()
    blurred_file = RelativeImageField(read_only=True)
    class Meta:
        model = PostFileContent
        fields = ['id', 'file', 'blurred_file', 'creation_date', 'update_date']
        read_only_fields = ['id', 'blurred_file']



class PostPostUpdateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Post
        fields = [
            'id', 'user_account', 'caption', 'plan',
            'is_open_to_comment', 'creation_date', 'update_date', 'files'
        ]


    def validate(self, attrs):
        request = self.context.get("request")
        uploaded_files = request.FILES.getlist("files") if request else []
        # Creation: must have at least one file

        # 🔒 Extract user_account from attrs
        user_account = attrs.get("user_account") or (self.instance.user_account if self.instance else None)

        # 🔒 Check ownership of plan
        plan = attrs.get("plan") or (self.instance.plan if self.instance else None)
        if plan and user_account and plan.user_account != user_account:
            raise serializers.ValidationError({
                "plan": "You do not have permission to use this plan."
            })

        if self.instance is None and len(uploaded_files) == 0:
            raise serializers.ValidationError({"files": "At least one file must be uploaded."})

        existing_count = self.instance.files.count() if self.instance else 0
        total_count = existing_count + len(uploaded_files)

        if total_count > 10:
            raise serializers.ValidationError({
                "files": f"Cannot upload {len(uploaded_files)} files. "
                         f"You already have {existing_count} files. "
                         f"Maximum total is 10."
            })
        
        attrs["uploaded_files"] = uploaded_files
        return attrs

    def create(self, validated_data):
        # uploaded_files was injected in validate()
        uploaded_files = validated_data.pop("uploaded_files", [])
        validated_data.pop("files", None)
        post = Post.objects.create(**validated_data)
        for file_obj in uploaded_files[:10]:  # limit max 10
            PostFileContent.objects.create(post=post, file=file_obj)
        return post

    def update(self, instance, validated_data):
        uploaded_files = validated_data.pop("uploaded_files", [])
        validated_data.pop("files", None)
        for attr in ["caption", "is_open_to_comment"]:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()

        if uploaded_files:
            existing_count = instance.files.count()
            # fill up to 10 files max
            for file_obj in uploaded_files[: max(0, 10 - existing_count)]:
                PostFileContent.objects.create(post=instance, file=file_obj)
        return instance




class PostRetrivalSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get('user', None)

    user_account = ExternalUserAccountRetrivalSerializer(read_only=True)
    files = PostFileContentSerializer(many=True, required=False)
    plan = ExternalPlanRetrivalSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()
    has_plan = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user_account', 'caption', 'plan',
            'is_open_to_comment', 'creation_date', 'update_date', 'files', 'is_owner', 'has_plan'
        ]


    def get_is_owner(self, obj):
        return self.user == obj.user_account if self.user else False

    def get_has_plan(self, obj):
        return self.user.is_superuser or obj.plan is None or (obj.plan is not None and obj.plan in self.user.plans.all())
