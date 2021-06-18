from .oijwt import jwt_decode_user_key

from django.apps import apps
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

import jwt
import logging

logger = logging.getLogger(__file__)


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason


class JWTAuthentication(BaseAuthentication):
    """
        class to obtain token from header if it is provided
        and verify if this is correct/valid token
    """

    def authenticate(self, request):
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return None
        payload = None
        if ' ' in authorization_header and 'Bearer' in authorization_header:
            bearer, access_token, *extra_words = authorization_header.split(' ')
            if bearer != 'Bearer':
                raise exceptions.AuthenticationFailed("Missing 'Bearer' prefix")
            if len(extra_words) > 0:
                raise exceptions.AuthenticationFailed("Unproper structure of token")
            try:
                payload = jwt_decode_user_key(token=access_token)
            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Access_token expired')
            except IndexError:
                raise exceptions.AuthenticationFailed('Token prefix missing')
            user = None
            if payload:
                user_class = apps.get_model("core", "User")
                user = user_class.objects \
                    .filter(username=payload.get("username")) \
                    .only("i_user__private_key") \
                    .first()
            if user is None:
                raise exceptions.AuthenticationFailed('User inactive or deleted/not existed.')
            if not user.is_active:
                raise exceptions.AuthenticationFailed('User is inactive')
        else:
            raise exceptions.AuthenticationFailed("Missing 'Bearer' prefix")

        self.enforce_csrf(request)

        return user, None


    def enforce_csrf(self, request):
        """
        Enforce CSRF validation
        """
        check = CSRFCheck()
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        logger.debug(reason)
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)

