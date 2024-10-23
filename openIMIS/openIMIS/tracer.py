import logging
from contextlib import contextmanager
from .settings import IS_SENTRY_ENABLED, DEBUG
import traceback

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
        path = ".".join([str(x) for x in info.path])
        # Start tracing
        with trace(op="graphql.resolve") as span:
            span.set_tag("path", path)  
            try:
                # Proceed with the next middleware or resolver
                return next(root, info, **kwargs)
            except Exception as e:
                # Log the exception with its traceback
                if DEBUG:
                    logger.error("An error occurred: %s", str(e))
                    logger.error("Traceback: %s", traceback.format_exc())
                
                # Optionally add error information to the trace
                span.set_tag("error", True)
                span.log_kv({"exception": str(e), "traceback": traceback.format_exc()})
                
                # Re-raise the exception to allow GraphQL to handle it
                raise e