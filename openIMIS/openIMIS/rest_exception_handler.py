from rest_framework import exceptions, status, views


def fhir_rest_api_exception_handler(exc, context):
    response = views.exception_handler(exc, context)

    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response