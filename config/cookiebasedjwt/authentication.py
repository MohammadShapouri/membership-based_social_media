from rest_framework_simplejwt.authentication import JWTAuthentication



class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        # Try to read token from "access" cookie
        raw_token = request.COOKIES.get("access")
        if raw_token is None:
            return None  # fallback to unauthenticated
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
