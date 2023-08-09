from .ExceptionHandlerRegistry import ExceptionHandlerRegistry
from rest_framework.views import exception_handler
from rest_framework import exceptions, status


def dispatcher(exc, context):
    """
    Dispatches the exception to the appropriate handler based on the module name.
    """
    module_name = _extract_module_name(context['request'])
    handler = ExceptionHandlerRegistry.get_exception_handler(module_name)

    if handler is None:
        # Fallback to default DRF exception handler if no handler is defined for the module
        handler = exception_handler

    response = handler(exc, context)
    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response


def _extract_module_name(request):
    """
    Extracts the module name from the request URL.
    """
    return request.path.split('/')[2]

