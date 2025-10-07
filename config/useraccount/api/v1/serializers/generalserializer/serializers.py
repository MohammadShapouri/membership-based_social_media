from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework import exceptions as rest_exceptions
from extentions.email_service.email_sender import send_otp_email
from django.contrib.auth.hashers import make_password
from otp.models import OTPCode, OTPTypeSetting
from useraccount.models import UserAccount
from rest_framework import serializers
from customserializers.serializers import RelativeImageField
from django.core import exceptions



class UserAccountDeletionSerializer(serializers.Serializer):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.requested_user = self.context.get('requested_user')
        self.fields['password'] = serializers.CharField(style = {'input_type': 'password'}, label='Old Password', write_only=True)

    def validate(self, attrs):
        # Get password from data.
        password = attrs.get('password')
        if not self.requested_user.check_password(password):
            raise serializers.ValidationError({'password': "Your password was entered incorrectly. Please enter it again."})
        return super().validate(attrs)





class ChangePasswordSerializer(serializers.Serializer):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.user = self.context.get('user')
        self.fields['old_password'] = serializers.CharField(style = {'input_type': 'password'}, label='Old Password', write_only=True)
        self.fields['new_password'] = serializers.CharField(style = {'input_type': 'password'}, label='New Password', write_only=True)
        self.fields['confirm_new_password'] = serializers.CharField(style = {'input_type': 'password'}, label='Repeated New Password', write_only=True)


    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.pop('confirm_new_password')
        errors_dict = dict()

        if not self.user.check_password(old_password):
            errors_dict['old_Password'] = "Your old password was entered incorrectly. Please enter it again."
        if new_password != confirm_new_password:
            errors_dict['new_password'] = "Two passwords aren't the same."

        try:
            # Validate the password and catch the exception
            validate_password(password=new_password, user=self.user)
        # The exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors_dict['new_password'] = list(e.messages)
        if errors_dict:
            raise serializers.ValidationError(errors_dict)
        return super().validate(attrs)


    def save(self, **kwargs):
        self.user.password = make_password(password=self.validated_data.get('new_password'))
        self.user.save()





class RequestResetPasswordOTPSerializer(serializers.Serializer):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.fields['email_username'] = serializers.CharField(required=True, label='Email or Username')





class VerifyResetPasswordOTPSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_username'] = serializers.CharField(required=True, label='Email or Username')
        self.fields['otp'] = serializers.CharField(required=True, label='OTP Code')

    def validate(self, attrs):
        otp = attrs.get('otp')
        if str.isdigit(otp) is False:
            raise serializers.ValidationError({'OTP': "OTP is not valid. It must not contain characters."})
        return super().validate(attrs)





class ResetPasswordOTPSerializer(serializers.Serializer):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.user = self.context.get('requested_user')
        self.fields['email_username'] = serializers.CharField(required=True, label='Email or Username')
        self.fields['otp'] = serializers.CharField(required=True, label='OTP Code')
        self.fields['new_password'] = serializers.CharField(style = {'input_type': 'password'}, label='New Password', write_only=True)
        self.fields['confirm_new_password'] = serializers.CharField(style = {'input_type': 'password'}, label='Confirm Password', write_only=True)


    def validate(self, attrs):
        otp = attrs.get('otp')
        if str.isdigit(otp) is False:
            raise serializers.ValidationError({'OTP': "OTP is not valid. It must not contain characters."})

        # Get passwords from data.
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.pop('confirm_new_password')
        errors_dict = dict()

        if new_password != confirm_new_password:
            errors_dict['new_password'] = "Two passwords aren't the same."

        try:
            # Validate the password and catch the exception
            validate_password(password=new_password, user=self.user)
        # The exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors_dict['new_password'] = list(e.messages)

        if errors_dict:
            raise serializers.ValidationError(errors_dict)

        return super().validate(attrs)


    def save(self, **kwargs):
        user = None
        try:
            if str(self.validated_data.get('email_username')).find('@') != -1:
                user = UserAccount.objects.get(email__iexact=self.validated_data.get('email_username'))
            else:
                user = UserAccount.objects.get(username__iexact=self.validated_data.get('email_username'))
        except UserAccount.DoesNotExist:
            return None
        user.password = make_password(password=self.validated_data.get('new_password'))
        user.save()




class ResetPasswordLinkSerializer(serializers.Serializer):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.user = self.context.get('user')
        self.fields['new_password'] = serializers.CharField(style = {'input_type': 'password'}, label='New Password', write_only=True)
        self.fields['confirm_new_password'] = serializers.CharField(style = {'input_type': 'password'}, label='Confirm Password', write_only=True)


    def validate(self, attrs):
        # Get passwords from data.
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.pop('confirm_new_password')
        errors_dict = dict()

        if new_password != confirm_new_password:
            errors_dict['new_password'] = "Two passwords aren't the same."

        try:
            # Validate the password and catch the exception
            validate_password(password=new_password, user=self.user)
        # The exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors_dict['new_password'] = list(e.messages)

        if errors_dict:
            raise serializers.ValidationError(errors_dict)

        return super().validate(attrs)


    def save(self, **kwargs):
        self.user.password = make_password(password=self.validated_data.get('new_password'))
        self.user.save()



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    authentication_error_messages = [
        {"no_account": "No account found with the given credentials."},
        {"no_active_account": "No active account found with the given credentials."},
        {"no_verified_account": "No verified account found with the given credentials. verification toekn sent to your email."}
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].label = 'Email or Username'


    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = None
        try:
            if str(authenticate_kwargs[self.username_field]).find('@') != -1:
                self.user = UserAccount.objects.get(email__iexact=authenticate_kwargs[self.username_field])
            else:
                self.user = UserAccount.objects.get(username__iexact=authenticate_kwargs[self.username_field])
        except UserAccount.DoesNotExist:
            raise rest_exceptions.AuthenticationFailed(self.authentication_error_messages[0])

        if not self.user.check_password(authenticate_kwargs["password"]):
            raise rest_exceptions.AuthenticationFailed(self.authentication_error_messages[0])

        if self.user.is_account_verified == False:
            otp_code, otp_object = OTPCode.objects.create_otp(OTPTypeSetting.objects.get(otp_type='timer_counter_based'), 'activate_account')
            self.user.otp_object = otp_object
            self.user.save()
            print("************", otp_code)
            send_otp_email.delay(otp_code)
            authentication_error_message = self.authentication_error_messages[2]
            authentication_error_message["id"] = int(self.user.id)
            raise rest_exceptions.AuthenticationFailed(authentication_error_message)
        else:
            if self.user.is_active == False:
                raise rest_exceptions.AuthenticationFailed(self.authentication_error_messages[1])

        attrs["username"] = self.user.username
        return super().validate(attrs)





class VerifyNewEmailVerificationOTPSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['otp'] = serializers.CharField(required=True, label='OTP Code')

    def validate(self, attrs):
        otp = attrs.get('otp')
        if str.isdigit(otp) is False:
            raise serializers.ValidationError({'OTP': "OTP is not valid. It must not contain characters."})
        return super().validate(attrs)





class VerifyAccountVerificationOTPSerializer(VerifyNewEmailVerificationOTPSerializer):
    pass







class CurrentUserAccountSerializer(serializers.ModelSerializer):
    profile_picture = RelativeImageField(required=False)
    background_picture = RelativeImageField(required=False)
    class Meta:
        model = UserAccount
        exclude = ['password', 'groups', 'user_permissions', 'otp_object']
    


class ExternalUserAccountRetrivalSerializer(serializers.ModelSerializer):
    profile_picture = RelativeImageField(required=False)
    background_picture = RelativeImageField(required=False)
    class Meta:
        model = UserAccount
        fields = ['id', 'full_name', 'username', 'profile_picture', 'background_picture', 'is_private', 'date_joined']
