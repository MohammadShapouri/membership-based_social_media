from django.db.models import Q
from useraccount.models import UserAccount
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from otp.models import OTPCode, OTPTypeSetting
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from extentions.email_service.email_sender import send_otp_email, send_link_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from .permissions import IsOwnerOrAdmin, IsOwner
from django_filters.rest_framework import DjangoFilterBackend
from .exceptions import (
                        NoExistingUser,
                        InactiveUser,
                        )
from useraccount.api.v1.serializers.generalserializer.serializers import (
                                                                    UserAccountDeletionSerializer,
                                                                    ChangePasswordSerializer,
                                                                    RequestResetPasswordOTPSerializer,
                                                                    VerifyResetPasswordOTPSerializer,
                                                                    ResetPasswordLinkSerializer,
                                                                    ResetPasswordOTPSerializer,
                                                                    VerifyNewEmailVerificationOTPSerializer,
                                                                    VerifyAccountVerificationOTPSerializer,
                                                                    CurrentUserAccountSerializer
                                                                    )
from useraccount.api.v1.serializers.normaluserserializer.serializers import (
                                                                    UserAccountCreationSerializer,
                                                                    UserAccountUpdateSerializer,
                                                                    UserAccountRetrivalSerializer
                                                                    )
from useraccount.api.v1.serializers.superuserserializer.serializers import (
                                                                    UserAccountCreationSerializer as SuperuserUserAccountCreationSerializer,
                                                                    UserAccountUpdateSerializer as SuperuserUserAccountUpdateSerializer,
                                                                    UserAccountRetrivalSerializer as SuperuserUserAccountRetrivalSerializer
                                                                    )
# Create your views here.



# Token stands for OTP or link in verification process.
# OTP stands for otp code in verification process.
# Link stands for verification link in verification process.
class UserAccountViewSet(ModelViewSet):
    queryset = UserAccount.objects.all()
    lookup_url_kwarg = 'pk'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'full_name']

    def get_queryset(self):
        if self.request.user.is_superuser:
            self.queryset = UserAccount.objects.all()
        else:
            self.queryset = UserAccount.objects.filter(Q(is_active=True) & Q(is_account_verified=True))
        return super().get_queryset()


    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = None
        obj = None
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            obj = queryset.get(**filter_kwargs)
        except UserAccount.DoesNotExist:
            raise NoExistingUser
        self.check_object_permissions(self.request, obj)

        if (self.request.user.is_authenticated and self.request.user.is_superuser) or (obj.is_active and obj.is_account_verified):
            return obj
        else:
            raise InactiveUser


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        if self.request.method not in ['POST', 'GET']:
            try:
                context.update({'requested_user': self.get_object()})
            except (NoExistingUser, InactiveUser):
                # Handle case where object doesn't exist or is inaccessible
                pass
        return context


    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'verify_new_email_by_otp':
            return VerifyNewEmailVerificationOTPSerializer
        elif hasattr(self, 'action') and self.action in ['change_password']:
            return ChangePasswordSerializer

        if self.request.user.is_authenticated and self.request.user.is_superuser:
            if self.request.method in ['PUT', 'PATCH']:
                return SuperuserUserAccountUpdateSerializer
            elif self.request.method == 'POST':
                return SuperuserUserAccountCreationSerializer
            elif self.request.method == 'DELETE':
                return UserAccountDeletionSerializer
            else:
                return SuperuserUserAccountRetrivalSerializer        
        else:
            if self.request.method in ['PUT', 'PATCH']:
                return UserAccountUpdateSerializer
            elif self.request.method == 'POST':
                return UserAccountCreationSerializer
            elif self.request.method == 'DELETE':
                return UserAccountDeletionSerializer
            else:
                return UserAccountRetrivalSerializer  


    def get_permissions(self):
        # Check if this is a custom action that requires IsOwnerOrAdmin permission
        if hasattr(self, 'action') and self.action in ['verify_new_email_by_otp', 'request_new_email_verification_token']:
            self.permission_classes = [IsOwnerOrAdmin]
        elif hasattr(self, 'action') and self.action in ['change_password']:
            self.permission_classes = [IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsOwnerOrAdmin]
        elif self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsOwnerOrAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


    def _get_otp_setting(self, otp_type):
        """Get OTP setting with caching to avoid repeated database queries."""
        if not hasattr(self, '_otp_settings_cache'):
            self._otp_settings_cache = {}
        
        if otp_type not in self._otp_settings_cache:
            try:
                self._otp_settings_cache[otp_type] = OTPTypeSetting.objects.get(otp_type=otp_type)
            except OTPTypeSetting.DoesNotExist:
                return None
        return self._otp_settings_cache[otp_type]


    def perform_create(self, serializer):
        """Handle user account creation with OTP verification."""
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            serializer.save()
        else:
            try:
                user: UserAccount = serializer.save(is_active=False, is_account_verified=False)                
                if settings.OTP_AS_VERIFICATION_METHOD:
                    # Get OTP setting and create OTP
                    otp_setting = self._get_otp_setting('timer_counter_based')
                    if otp_setting:
                        otp_code, otp_object = OTPCode.objects.create_otp(otp_setting, 'activate_account')
                        user.otp_object = otp_object
                        user.save()
                        
                        print("*********", otp_code)
                        # Send OTP email asynchronously
                        send_otp_email.delay(otp_code)
                    else:
                        # Handle case where OTP setting doesn't exist
                        user.delete()
                        raise Exception("OTP configuration not found")
                else:
                    user.save()
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    verification_link = settings.FRONTEND_DOMAIN + f"/verify-account?uid={uid}&token={token}"
                    # Send OTP email asynchronously
                    print(verification_link)
                    send_link_email.delay(verification_link)

            except Exception as e:
                # Log error and provide user-friendly message
                raise Exception(f"Failed to create account: {str(e)}")


    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            response.data['account_verification'] = "For verifying your account, please check your email."
        return response


    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if not response.data.get("is_new_email_verified", True):
            response.data['new_email_verification'] = "For verifying your new email, please check your new email inbox."
        return response


    def perform_update(self, serializer):
        """Handle user account updates with email verification if needed."""
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            serializer.save(is_active=True, is_account_verified=True)
        else:
            # Check if email is being updated
            new_email = serializer.validated_data.get('email')
            old_email = serializer.instance.email
            if new_email and new_email != old_email:
                user = None
                serializer.validated_data['new_email'] = new_email
                serializer.validated_data['email'] = old_email
                user = serializer.save(is_new_email_verified=False)                    
                if settings.OTP_AS_VERIFICATION_METHOD:
                    # Get OTP setting and create OTP for email verification
                    otp_setting = self._get_otp_setting('counter_based')
                    if otp_setting:
                        otp_code, otp_object = OTPCode.objects.create_otp(otp_setting, 'update_account')
                        user.otp_object = otp_object
                        user.save()

                        print("************", otp_code)
                        # Send OTP email asynchronously to the new email address
                        send_otp_email.delay(otp_code)
                        # Don't save the serializer yet - we'll save other fields separately
                    else:
                        # Handle case where OTP setting doesn't exist
                        raise Exception("OTP configuration not found")   
                else:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    verification_link = settings.FRONTEND_DOMAIN + f"/verify-email?uid={uid}&token={token}"
                    # Send OTP email asynchronously
                    print(verification_link)
                    send_link_email.delay(verification_link)
            else:
                serializer.save()


    def perform_destroy(self, instance):
        """Handle user account deletion with validation."""
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        # The serializer validation ensures the request data is valid
        # Now proceed with deletion
        return super().perform_destroy(instance)


    def verify_new_email_by_otp(self, request, *args, **kwargs):
        """Verify and activate the new email address after OTP verification."""
        # Get the user object first
        user = self.get_object()
        
        # Check object permissions (this will enforce IsOwnerOrAdmin)
        self.check_object_permissions(request, user)
        
        # Check if user has a pending new email verification
        if not user.new_email or user.is_new_email_verified:
            return Response({'error': 'No pending email verification found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is valid
        if not user.otp_object:
            return Response({'error': 'No OTP found for email verification'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use serializer for validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get validated OTP from serializer
        otp_code = serializer.validated_data['otp']
        
        result, error_title, error_desc = user.otp_object.check_otp(otp_code, 'update_account')
        
        if result:
            # OTP is valid, update the email
            old_email = user.email
            user.email = user.new_email
            user.new_email = None
            user.is_new_email_verified = True
            user.save()
            user.otp_object.delete()
            
            return Response({
                'success': 'Email updated successfully',
                'old_email': old_email,
                'new_email': user.email
            }, status=status.HTTP_200_OK)
        else:
            # Handle OTP errors
            if error_title == 'wrong_opt_code':
                return Response({'error': 'OTP is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            elif error_title == 'max_attempt_exceeded':
                return Response({'error': 'Max attempts exceeded for this OTP code. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
            elif error_title == 'expired':
                return Response({'error': 'OTP is expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': f'OTP verification failed: {error_title}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def request_new_email_verification_token(self, request, *args, **kwargs):
        """Request new email verification Token for pending email change."""
        # Get the user object first
        user: UserAccount = self.get_object()

        # Check object permissions (this will enforce IsOwnerOrAdmin)
        self.check_object_permissions(request, user)
        
        # Check if user has a pending new email verification
        if not user.new_email or user.is_new_email_verified:
            return Response({'error': 'No pending email verification found'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if settings.OTP_AS_VERIFICATION_METHOD:
                # Get OTP setting and create new OTP for email verification
                otp_setting = self._get_otp_setting('counter_based')
                if otp_setting:
                    # Delete existing OTP if any
                    if user.otp_object:
                        user.otp_object.delete()
                    
                    # Create new OTP
                    otp_code, otp_object = OTPCode.objects.create_otp(otp_setting, 'update_account')
                    user.otp_object = otp_object
                    user.save()

                    print("************", otp_code)
                    # Send OTP email asynchronously to the new email address
                    send_otp_email.delay(otp_code)
                    return Response({
                        'success': 'Email verification OTP sent successfully',
                        'message': 'Please check your new email inbox for the verification code.',
                        'id': user.id
                    }, status=status.HTTP_200_OK)
                else:
                    raise Exception("OTP configuration not found")
            else:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_link = settings.FRONTEND_DOMAIN + f"/verify-email?uid={uid}&token={token}"
                # Send OTP email asynchronously
                print("****************", verification_link)
                send_link_email.delay(verification_link)
                return Response({
                    'success': 'Email verification link sent successfully',
                    'message': 'Please check your new email inbox for the verification link.'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({'error': f'Failed to send OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def change_password(self, request, *args, **kwargs):
        """Change user account password."""
        # Get the user object first
        user = self.get_object()
        
        # Check object permissions (this will enforce IsOwnerOrAdmin)
        self.check_object_permissions(request, user)
        
        # Check if user is active and verified
        if not user.is_active or not user.is_account_verified:
            raise InactiveUser()
        
        # Use the ChangePasswordSerializer for validation
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        
        # Save the new password
        serializer.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)





class RequestResetPasswordTokenView(GenericAPIView):
    """View for requesting password reset OTP."""
    serializer_class = RequestResetPasswordOTPSerializer
    permission_classes = [AllowAny]
    email_username = None

    def get_object(self):
        user = None
        try:
            if str(self.email_username).find('@') != -1:
                user = UserAccount.objects.get(email__iexact=self.email_username)
            else:
                user = UserAccount.objects.get(username__iexact=self.email_username)
        except UserAccount.DoesNotExist:
            return None
        if not user.is_active and user.is_account_verified:
            raise InactiveUser()
        return user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.email_username = serializer.validated_data['email_username']
        user = self.get_object()
        # Only generates and sends OTP code to existing accounts which are active.
        if user is not None:
            if settings.OTP_AS_VERIFICATION_METHOD:
                otp_code, otp_object = OTPCode.objects.create_otp(OTPTypeSetting.objects.get(otp_type='timer_counter_based'), 'reset_password')
                user.otp_object = otp_object
                user.save()
                print("************", otp_code)
                send_otp_email.delay(otp_code)
            else:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_link = settings.FRONTEND_DOMAIN + f"/reset-password?uid={uid}&token={token}"
                # Send OTP email asynchronously
                print("************", verification_link)
                send_link_email.delay(verification_link)
        return Response({'detail': "Reset password token will be sent to your email."}, status.HTTP_200_OK)





class VerifyResetPasswordOTPView(GenericAPIView):
    serializer_class = VerifyResetPasswordOTPSerializer
    permission_classes = [AllowAny]
    email_username = None

    def get_object(self):
        user = None
        try:
            if str(self.email_username).find('@') != -1:
                user = UserAccount.objects.get(email__iexact=self.email_username)
            else:
                user = UserAccount.objects.get(username__iexact=self.email_username)
        except UserAccount.DoesNotExist:
            return None
        if not user.is_active and user.is_account_verified:
            raise InactiveUser()
        return user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']
        self.email_username = serializer.validated_data['email_username']
        user = self.get_object()

        if user is not None:
            if user.otp_object is None:
                return Response({'OTP': "No OTP code found."}, status.HTTP_404_NOT_FOUND)

            result, error_title, error_desc = user.otp_object.check_otp(otp, 'reset_password')
            if result:
                return Response({'OTP': "OTP is correct."}, status.HTTP_200_OK)
            else:
                if error_title == 'wrong_opt_code':
                    return Response({'OTP': "OTP is wrong."}, status.HTTP_400_BAD_REQUEST)
                elif error_title == 'max_attempt_exceeded':
                    return Response({'OTP': "Max attempts exceeded for this otp code. request new one"}, status.HTTP_400_BAD_REQUEST)
                elif error_title == 'expired':
                    return Response({'OTP': "OTP is expired."}, status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'OTP': error_title}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'detail': "OTP code is wrong."}, status.HTTP_400_BAD_REQUEST)






class ResetPasswordOTPView(GenericAPIView):
    serializer_class = ResetPasswordOTPSerializer
    permission_classes = [AllowAny]
    email_username = None

    def get_object(self):
        user = None
        try:
            if str(self.email_username).find('@') != -1:
                user = UserAccount.objects.get(email__iexact=self.email_username)
            else:
                user = UserAccount.objects.get(username__iexact=self.email_username)
        except UserAccount.DoesNotExist:
            return None
        if not user.is_active and user.is_account_verified:
            raise InactiveUser()
        return user


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']
        self.email_username = serializer.validated_data['email_username']
        user = self.get_object()

        if user is not None:
            if user.otp_object is None:
                return Response({'OTP': "No OTP code found."}, status.HTTP_404_NOT_FOUND)

            result, error_title, error_desc = user.otp_object.check_otp(otp, 'reset_password')
            if result:
                serializer.save()
                user.otp_object.delete()
                return Response({'detail': "Password reset successfully."}, status.HTTP_200_OK)
            else:
                if error_title == 'wrong_opt_code':
                    return Response({'OTP': "OTP is wrong."}, status.HTTP_400_BAD_REQUEST)
                elif error_title == 'max_attempt_exceeded':
                    return Response({'OTP': "Max attempts exceeded for this otp code. request new one"}, status.HTTP_400_BAD_REQUEST)
                elif error_title == 'expired':
                    return Response({'OTP': "OTP is expired."}, status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'OTP': error_title}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'detail': "OTP code is wrong."}, status.HTTP_400_BAD_REQUEST)





class VerifyAccountVerificationOTPView(GenericAPIView):
    serializer_class = VerifyAccountVerificationOTPSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'pk'

    def get_object(self):
        user = None
        try:
            pk = self.kwargs[self.lookup_url_kwarg]
            user = UserAccount.objects.get(pk=pk)
        except UserAccount.DoesNotExist:
            return None
        self.check_object_permissions(self.request, user)
        return user

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']
        user = self.get_object()

        if user != None:
            if user.otp_object == None:
                return Response({'OTP': "No OTP code found."}, status.HTTP_404_NOT_FOUND)

            result, error_title, error_desc = user.otp_object.check_otp(otp, 'activate_account')
            if result:
                return self.correct_otp_actions(user, serializer)
            else:
                if error_title == 'wrong_opt_code':
                    return Response({'OTP': "OTP is wrong."}, status.HTTP_400_BAD_REQUEST)
                elif error_title == 'max_attempt_exceeded':
                    return Response({'OTP': "Max attempts exceeded for this otp code. request new one"}, status.HTTP_400_BAD_REQUEST)
                elif error_title == 'expired':
                    return Response({'OTP': "OTP is expired."}, status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'OTP': error_title}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'detail': "OTP code is wrong."}, status.HTTP_400_BAD_REQUEST)


    def correct_otp_actions(self, user, serializer):
        user.is_active = True
        user.is_account_verified = True
        user.save()
        user.otp_object.delete()
        return Response({'OTP': "OTP is correct. Account verified."}, status.HTTP_200_OK)



class VerifyAccountVerificationLinkView(APIView):
    def get(self, request, *args, **kwargs):
        uidb64 = request.query_params.get("uid")
        token = request.query_params.get("token")
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserAccount.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
            return Response({"success": False, "message": "Invalid user."}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_account_verified = True
            user.save()
            return Response({"success": True, "message": "Account verified successfully."})
        else:
            return Response({"success": False, "message": "Invalid or expired token."}, status=400)





class VerifyNewEmailLinkView(APIView):
    def get(self, request, *args, **kwargs):
        uidb64 = request.query_params.get("uid")
        token = request.query_params.get("token")
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserAccount.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
            return Response({"success": False, "message": "Invalid user."}, status=400)

        if default_token_generator.check_token(user, token):
            if user.is_new_email_verified or not user.new_email:
                return Response({
                    'success': 'New email is already verified.',
                    'new_email': user.email
                }, status=status.HTTP_200_OK)
            # OTP is valid, update the email
            old_email = user.email
            user.email = user.new_email
            user.new_email = None
            user.is_new_email_verified = True
            user.save()
            return Response({
                'success': 'Email updated successfully',
                'old_email': old_email,
                'new_email': user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Invalid or expired token."}, status=400)





class VerifyResetPasswordLinkView(APIView):
    def get(self, request, *args, **kwargs):
        uidb64 = request.query_params.get("uid")
        token = request.query_params.get("token")
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserAccount.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
            return Response({"success": False, "message": "Invalid user."}, status=400)

        if default_token_generator.check_token(user, token):
            # OTP is valid, update the email
            return Response({
                'success': True,
                'success': 'Link is valid.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Invalid or expired token."}, status=400)





class ResetPasswordLinkView(GenericAPIView):
    serializer_class = ResetPasswordLinkSerializer
    permission_classes = [AllowAny]
    user = None


    def post(self, request, *args, **kwargs):
        uidb64 = request.query_params.get("uid")
        token = request.query_params.get("token")
        if not uidb64 or not token:
            return Response({"success": False, "message": "Invalid link."}, status=400)
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            self.user = UserAccount.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
            return Response({"success": False, "message": "Invalid user."}, status=400)

        serializer = self.get_serializer(data=request.data, context={'user': self.user})
        serializer.is_valid(raise_exception=True)

        if default_token_generator.check_token(self.user, token):
            serializer.save()
            return Response({
                'success': 'Password updated successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": "Invalid or expired token."}, status=400)




class CurrentUserAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserAccountSerializer(request.user)
        return Response(serializer.data)
