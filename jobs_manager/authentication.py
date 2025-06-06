from django.conf import settings
from rest_framework_simplejwt.authentication import (
    JWTAuthentication as BaseJWTAuthentication,
)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework import exceptions


class JWTAuthentication(BaseJWTAuthentication):
    """
    Custom JWT Authentication that supports both Authorization header and httpOnly cookies.
    """

    def authenticate(self, request):
        if not getattr(settings, "ENABLE_JWT_AUTH", False):
            return None

        try:
            # First try to get token from Authorization header (default behavior)
            result = super().authenticate(request)
            
            # If no token in header, try to get from httpOnly cookie
            if result is None:
                raw_token = self.get_raw_token_from_cookie(request)
                if raw_token is not None:
                    validated_token = self.get_validated_token(raw_token)
                    user = self.get_user(validated_token)
                    result = (user, validated_token)

            if result is None:
                return None

            user, token = result

            if not user.is_active:
                raise exceptions.AuthenticationFailed(
                    "User is inactive.", code="user_inactive"
                )

            if hasattr(user, "password_needs_reset") and user.password_needs_reset:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"User {user.email} authenticated via JWT but needs to reset password."
                )

            return result

        except (InvalidToken, TokenError) as e:
            if getattr(settings, "ENABLE_DUAL_AUTHENTICATION", False):
                return None

            raise exceptions.AuthenticationFailed(str(e))

    def get_raw_token_from_cookie(self, request):
        """
        Extract raw token from httpOnly cookie.
        """
        cookie_name = jwt_settings.AUTH_COOKIE
        if cookie_name and cookie_name in request.COOKIES:
            return request.COOKIES[cookie_name].encode('utf-8')
        return None
