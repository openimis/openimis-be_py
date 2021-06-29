# from graphql_auth.backends import GraphQLAuthBackend
# from django.utils.deprecation import MiddlewareMixin
import jwt
from graphql_jwt.settings import jwt_settings
from django.apps import apps

import logging

logger = logging.getLogger(__file__)


def jwt_encode_user_key(payload, context=None):
    token = jwt.encode(
        payload,
        get_jwt_key(encode=True, context=context),
        jwt_settings.JWT_ALGORITHM,
    )
    # JWT module after 1.7 does the encoding, introducing some conflicts in graphql-jwt, let's support both
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def jwt_decode_user_key(token, context=None):
    # First decode the token without validating it, so we can extract the username
    not_validated = jwt.decode(
        token,
        get_jwt_key(encode=False, context=context),
        options={
            'verify_exp': jwt_settings.JWT_VERIFY_EXPIRATION,
            'verify_aud': jwt_settings.JWT_AUDIENCE is not None,
            'verify_signature': False,
        },
        leeway=jwt_settings.JWT_LEEWAY,
        audience=jwt_settings.JWT_AUDIENCE,
        issuer=jwt_settings.JWT_ISSUER,
        algorithms=[jwt_settings.JWT_ALGORITHM],
    )
    if not_validated and not_validated.get("username"):
        user_class = apps.get_model("core", "User")
        db_user = user_class.objects\
            .filter(username=not_validated.get("username"))\
            .only("i_user__private_key")\
            .first()
        if db_user and db_user.private_key:
            key = db_user.private_key
        else:
            key = get_jwt_key(encode=False)
    else:
        key = get_jwt_key(encode=False)
    return jwt.decode(
        token,
        key,
        options={
            'verify_exp': jwt_settings.JWT_VERIFY_EXPIRATION,
            'verify_aud': jwt_settings.JWT_AUDIENCE is not None,
            'verify_signature': jwt_settings.JWT_VERIFY,
        },
        leeway=jwt_settings.JWT_LEEWAY,
        audience=jwt_settings.JWT_AUDIENCE,
        issuer=jwt_settings.JWT_ISSUER,
        algorithms=[jwt_settings.JWT_ALGORITHM],
    )


def get_jwt_key(encode=True, context=None):
    user_key = extract_private_key_from_context(context)
    if user_key:
        return user_key
    if encode:
        if hasattr(jwt_settings, "JWT_PRIVATE_KEY"):
            return jwt_settings.JWT_PRIVATE_KEY
    else:
        if hasattr(jwt_settings, "JWT_PUBLIC_KEY"):
            return jwt_settings.JWT_PUBLIC_KEY
    return jwt_settings.JWT_SECRET_KEY


def extract_private_key_from_context(context):
    if context and context.user and hasattr(context.user, "private_key"):
        return context.user.private_key
    return None

