from django.db import connection, transaction
from django.http import HttpResponseNotAllowed
from django.http.response import HttpResponseBadRequest
from .dataloaders import get_dataloaders
from . import tracer
from graphql.execution import ExecutionResult

from graphene_django.constants import MUTATION_ERRORS_FLAG
from graphene_django.utils.utils import set_rollback
from graphql_jwt.exceptions import JSONWebTokenError
from graphene_django.settings import graphene_settings
from graphene_django.views import GraphQLView as BaseGraphQLView, HttpError
import logging

logger = logging.getLogger(__name__)


def has_jwt_error(errors):
    for error in errors:
        if isinstance(getattr(error, "original_error", None), JSONWebTokenError):
            return True
    return False


class GraphQLView(BaseGraphQLView):
    def json_encode(self, request, d, pretty=False):
        with tracer.trace(op="GraphQLView.json_encode"):
            return super().json_encode(request, d, pretty=pretty)

    def _get_response(self, request, data, show_graphiql=False):
        query, variables, operation_name, id = self.get_graphql_params(request, data)

        execution_result = self.execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )

        if getattr(request, MUTATION_ERRORS_FLAG, False) is True:
            set_rollback()

        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                set_rollback()
                response["errors"] = [
                    self.format_error(e) for e in execution_result.errors
                ]

            if execution_result.invalid:
                status_code = 400
            elif execution_result.errors and has_jwt_error(execution_result.errors):
                status_code = 401
            else:
                response["data"] = execution_result.data

            if self.batch:
                response["id"] = id
                response["status"] = status_code

            result = self.json_encode(request, response, pretty=show_graphiql)
        else:
            result = None

        return result, status_code

    def get_response(self, request, data, show_graphiql=False):
        with tracer.trace(op="GraphQLView.get_response") as span:
            result, status_code = self._get_response(
                request, data, show_graphiql=show_graphiql
            )
            span.set_tag("status_code", status_code)
        return result, status_code

    def get_context(self, request):
        request.dataloaders = get_dataloaders()
        return request

    def parse_body(self, request):
        with tracer.trace(op="GraphQLView.parse_body") as span:
            request_json = super().parse_body(request)
            span.set_data("Body", request_json)
            return request_json

    def execute_graphql_request(
        self, request, data, query, variables, operation_name, show_graphiql=False
    ):
        if not query:
            if show_graphiql:
                return None
            raise HttpError(HttpResponseBadRequest("Must provide query string."))

        try:
            backend = self.get_backend(request)
            with tracer.trace(op="backend.document_from_string"):
                document = backend.document_from_string(self.schema, query)
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

        if request.method.lower() == "get":
            operation_type = document.get_operation_type(operation_name)
            if operation_type and operation_type != "query":
                if show_graphiql:
                    return None

                raise HttpError(
                    HttpResponseNotAllowed(
                        ["POST"],
                        "Can only perform a {} operation from a POST request.".format(
                            operation_type
                        ),
                    )
                )

        try:
            extra_options = {}
            if self.executor:
                # We only include it optionally since
                # executor is not a valid argument in all backends
                extra_options["executor"] = self.executor

            options = {
                "root_value": self.get_root_value(request),
                "variable_values": variables,
                "operation_name": operation_name,
                "context_value": self.get_context(request),
                "middleware": self.get_middleware(request),
            }
            options.update(extra_options)

            operation_type = document.get_operation_type(operation_name)
            if operation_type == "mutation" and (
                graphene_settings.ATOMIC_MUTATIONS is True
                or connection.settings_dict.get("ATOMIC_MUTATIONS", False) is True
            ):
                with transaction.atomic():
                    result = document.execute(**options)
                    if getattr(request, MUTATION_ERRORS_FLAG, False) is True:
                        transaction.set_rollback(True)
                return result
            with tracer.trace(op="document.execute"):
                return document.execute(**options)
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)


class OpenIMISGraphQLView(GraphQLView):
    def execute_graphql_request(self, *args, **kwargs):
        """Extract any exceptions and send them to Sentry"""
        result = super().execute_graphql_request(*args, **kwargs)
        if result.errors:
            self._capture_sentry_exceptions(result.errors)
        return result

    def _capture_sentry_exceptions(self, errors):
        for error in errors:
            try:
                logger.error(error.original_error)
            except AttributeError:
                logger.error(error)
