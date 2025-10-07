from useraccount.models import UserAccount
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from customserializers.serializers import RelativeImageField
from django.core import exceptions
from django.db.models import Q


class UserAccountCreationSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'].read_only = True
        self.fields['password'].write_only = True
        self.fields['is_active'].read_only = True
        self.fields['is_account_verified'].read_only = True
        self.fields['date_joined'].read_only = True

    confirm_password = serializers.CharField(style = {'input_type': 'password'}, label='Repeated Password', write_only=True)

    class Meta:
        model = UserAccount
        fields = ['id', 'full_name', 'username', 'email', 'password', 'confirm_password', 'is_active', 'date_joined', 'is_account_verified']


    def validate(self, attrs):
        # Get passwords from data.
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password')
        errors_dict = dict()

        if password != confirm_password:
            errors_dict['password'] = "Two passwords aren't the same."
        # Here data has all the fields which have validated values.
        # So we can create a User instance out of it.
        user = UserAccount(**attrs)
        try:
            # Validate the password and catch the exception
            validate_password(password=password, user=user)
        # The exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors_dict['password'] = list(e.messages)
        if errors_dict:
            raise serializers.ValidationError(errors_dict)
        
        # if self.request.data.get('is_account_verified') == None or self.request.data.get('is_account_verified') == '':
        #     attrs['is_account_verified'] = False
        return super().validate(attrs)

    def save(self, **kwargs):
        self.validated_data['password'] = make_password(password=self.validated_data.get('password'))
        return super().save(**kwargs)





class UserAccountUpdateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'].read_only = True
        self.fields['new_email'].read_only = True
        self.fields['is_new_email_verified'].read_only = True
        self.fields['date_joined'].read_only = True
        self.fields['profile_picture'] = RelativeImageField(required=False)
        self.fields['background_picture'] = RelativeImageField(required=False)
        
    class Meta:
        model = UserAccount
        fields = ['id', 'full_name', 'username', 'email', 'profile_picture', 'background_picture', 'is_private', 'date_joined', 'new_email', 'is_new_email_verified']


    def validate(self, attrs):
        if attrs.get('email', None) is not None:
            if attrs['email'] != self.instance.email:
                new_email = attrs['email']
                user = UserAccount.objects.filter(~Q(pk=self.instance.pk) & (Q(new_email = new_email) | Q(email = new_email)))
                if user.exists():
                    model_name = UserAccount._meta.verbose_name.title()
                    field_name = UserAccount._meta.get_field('email').verbose_name.title()
                    raise serializers.ValidationError({'Email': f"{model_name} with this {field_name} already exists."})
        return super().validate(attrs)





class UserAccountRetrivalSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get('user')
        self.requested_user = self.context.get('requested_user')
        self.fields['profile_picture'] = RelativeImageField(required=False)
        self.fields['background_picture'] = RelativeImageField(required=False)
        fields = ['id', 'full_name', 'username', 'profile_picture', 'background_picture']
        if self.user.is_authenticated and str(self.user) == str(self.requested_user):
            fields = ['id', 'full_name', 'username', 'email', 'profile_picture', 'background_picture', 'is_private', 'last_login', 'new_email', 'is_new_email_verified', 'date_joined']


        allowed = set(fields)
        existing = set(self.fields.keys())
        for field_name in existing - allowed:
            self.fields.pop(field_name)

    class Meta:
        model = UserAccount
        fields = ['id', 'full_name', 'username', 'email', 'last_login', 'profile_picture', 'background_picture', 'is_private', 'date_joined', 'new_email', 'is_new_email_verified']
