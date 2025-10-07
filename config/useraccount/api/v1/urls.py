from django.urls import path
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('users', views.UserAccountViewSet, basename='user-account')


urlpatterns = [
    # Change password URL.
    path('users/<int:pk>/change-password', views.UserAccountViewSet.as_view({'post': 'change_password'}), name='change-password'),
    # Reset password URLs. --- VALID FOR BOTH OTP AND LINK. ---
    path('request-reset-password-token', views.RequestResetPasswordTokenView.as_view(), name='request-reset-password-token'),
    # Verifications reset password URLs. --- VALID ONLY FOR OTP. ---
    path('verify-reset-password-otp', views.VerifyResetPasswordOTPView.as_view(), name='verify-reset-password-otp'),
    # Reset password URLs. --- VALID ONLY FOR OTP. ---
    path('otp-reset-password', views.ResetPasswordOTPView.as_view(), name='otp-reset-password'),
    # Verifications account URLs. --- VALID ONLY FOR OTP. ---
    path('users/<int:pk>/verify-account', views.VerifyAccountVerificationOTPView.as_view(), name='verify-account-by-otp'),
    # Request new email verification OTP URL. --- VALID FOR BOTH OTP AND LINK. ---
    path('users/<int:pk>/request-new-email-verification-token', views.UserAccountViewSet.as_view({'post': 'request_new_email_verification_token'}), name='request-new-email-verification-token'),
    # New email verification URL. --- VALID ONLY FOR OTP. ---
    path('users/<int:pk>/verify-new-email', views.UserAccountViewSet.as_view({'post': 'verify_new_email_by_otp'}), name='verify-new-email-by-otp'),
    # Verifications account URLs. --- VALID ONLY FOR link. ---
    path('verify-account', views.VerifyAccountVerificationLinkView.as_view(), name='verify-account-by-link'),
    # Verifications email URLs. --- VALID ONLY FOR link. ---
    path('verify-email', views.VerifyNewEmailLinkView.as_view(), name='verify-email-by-link'),

    # Verifications reset password URLs. --- VALID ONLY FOR link. ---
    path('reset-password', views.VerifyResetPasswordLinkView.as_view(), name='verify-reset-password-link'),
    # Reset password URLs. --- VALID ONLY FOR link. ---
    path('link-reset-password', views.ResetPasswordLinkView.as_view(), name='link-reset-password'),
    # 
    path("auth/me/", views.CurrentUserAccountView.as_view(), name="auth-me"),
]
urlpatterns += router.urls
