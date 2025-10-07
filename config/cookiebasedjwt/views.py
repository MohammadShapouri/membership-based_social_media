from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class CookieBasedTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data
        access = data.get("access")
        refresh = data.get("refresh")

        # Set HttpOnly cookies
        res = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        res.set_cookie(
            key="access",
            value=access,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax" if settings.DEBUG else "Strict",
            max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        )
        res.set_cookie(
            key="refresh",
            value=refresh,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax" if settings.DEBUG else "Strict",
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        )
        return res
