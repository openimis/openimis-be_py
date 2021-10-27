import logging
from contextlib import contextmanager
from .settings import IS_SENTRY_ENABLED

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
except ModuleNotFoundError:
    sentry_sdk = None


class FakeSpan:
    def set_tag(self, *args, **kwargs):
        pass

    def set_data(self, *args, **kwargs):
        pass


@contextmanager
def trace(*args, **kwargs):
    if IS_SENTRY_ENABLED:
        with sentry_sdk.start_span(*args, **kwargs) as span:
            yield span
    else:
        yield FakeSpan()


class TracerMiddleware:
    def resolve(self, next, root, info, **kwargs):

        parent_type_name = (
            root._meta.name
            if root and hasattr(root, "_meta") and hasattr(root._meta, "name")
            else ""
        )
        field_name = (
            parent_type_name + ("." if parent_type_name else "") + info.field_name
        )
        with trace(op=f"graphql.resolve.{field_name}") as span:
            span.set_tag("field_name", field_name)
            return next(root, info, **kwargs)
