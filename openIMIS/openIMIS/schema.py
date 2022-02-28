import graphene

from core.models import Language
from django.utils import translation

from .openimisapps import openimis_apps
from graphene_django.debug import DjangoDebug

import logging

logger = logging.getLogger(__name__)

all_apps = openimis_apps()
queries = []
mutations = []
bind_signals = []
for app in all_apps:
    try:
        # If we only __import__ the module, the schema is not loaded and .schema will fail. Adding an import to force
        # Python to load it would work but not from __init__.py because Django models are not loaded yet at that point.
        # Importing claim.schema still returns the claim module but it forces the loading of schema.
        # This code is executed on first access to the Graphene API
        schema = __import__(f"{app}.schema")
        if hasattr(schema.schema, "Query"):
            queries.append(schema.schema.Query)
            logger.debug(f"{app} queries loaded")
        if hasattr(schema.schema, "bind_signals"):
            bind_signals.append(schema.schema.bind_signals)
            logger.debug(f"{app} signals bound")
    except ModuleNotFoundError as exc:
        # The module doesn't have a schema.py, just skip
        logger.debug(f"{app} has no schema module, skipping")
    except AttributeError as exc:
        logger.debug(f"{app} queries couldn't be loaded")
        raise  # This can be hiding actual compilation errors
    except Exception as exc:
        logger.debug(f"{app} exception", exc)

    try:
        schema_module = __import__(f"{app}.schema")
        if hasattr(schema_module.schema, "Mutation"):
            mutation = schema_module.schema.Mutation
            if mutation:
                mutations.append(mutation)
                logger.debug(f"{app} mutations loaded")
        else:
            logger.debug(f"{app} has a schema module but no Mutation class")
    except ModuleNotFoundError as exc:
        # The module doesn't have a schema.py, just skip
        logger.debug(f"{app} has no schema module (mutation), skipping")
    except AttributeError as exc:
        # The module doesn't have a Query or Mutation, just ignore
        logger.debug(f"{app} has a schema module and Mutation but failed nonetheless")

    for binder in bind_signals:
        binder()


class Query(*queries, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")
    node = graphene.relay.Node.Field()


class Mutation(*mutations, graphene.ObjectType):
    pass


class GQLUserLanguageMiddleware:
    def resolve(self, next_middleware, root, info, **kwargs):
        if info and info.context and info.context.user and hasattr(info.context.user, "language") \
                and info.context.user.language:
            lang = info.context.user.language
            if isinstance(lang, Language):
                translation.activate(lang.code)
            else:
                translation.activate(lang)
        return next_middleware(root, info, **kwargs)


# noinspection PyTypeChecker
schema = graphene.Schema(query=Query, mutation=Mutation if len(mutations) > 0 else None)
