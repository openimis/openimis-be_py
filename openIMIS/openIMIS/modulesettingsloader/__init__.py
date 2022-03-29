import logging
import os
import sys

import typing

from ..openimisapps import openimis_apps
from .settings_attributes import SettingsAttribute, SettingsAttributeConflictPolicy
from .conflict_resolve_strategies import REGISTERED_STRATEGIES
logger = logging.getLogger(__name__)


class SettingAttributeConflictResolver:
    @classmethod
    def resolve_conflict(
            cls, existing_attribute: typing.Union[None, SettingsAttribute], new_attribute: SettingsAttribute):
        resolving_policy = cls.get_conflict_resolve_policy(existing_attribute, new_attribute)
        return resolving_policy(existing_attribute, new_attribute)

    @classmethod
    def get_conflict_resolve_policy(cls, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute):
        for registered_resolving_strategy in REGISTERED_STRATEGIES:
            if registered_resolving_strategy.is_strategy_matching(existing_attribute, new_attribute):
                return registered_resolving_strategy.resolve_conflict


class ModulesSettingsLoader:
    @classmethod
    def load_settings_extensions(cls):
        resolved_settings = cls._resolve_settings()
        for attribute in resolved_settings:
            setattr(sys.modules['openIMIS.settings'], attribute.SETTING_NAME, attribute.SETTING_VALUE)

    @classmethod
    def _resolve_settings(cls) -> typing.Iterable[SettingsAttribute]:
        openimis_apps_extensions = cls._settings_extensions()
        resolved_settings = {}
        for module, settings in openimis_apps_extensions.items():
            for setting in settings:
                if setting.SETTING_NAME not in resolved_settings:
                    resolved_settings[setting.SETTING_NAME] = setting
                else:
                    resolved_settings[setting.SETTING_NAME] = SettingAttributeConflictResolver\
                        .resolve_conflict(resolved_settings[setting.SETTING_NAME], setting)
        return resolved_settings.values()

    @classmethod
    def _settings_extensions(cls) -> typing.Dict[str, typing.Iterable[SettingsAttribute]]:
        out = {}
        modules = ['openIMIS', *openimis_apps()]  # Assembly + installed modules
        for module in modules:
            if setting_extension := cls._get_module_setting_extension(module):
                out[module] = setting_extension
        return out

    @classmethod
    def _get_module_setting_extension(cls, app_):
        module_settings_extension = None
        try:
            settings_extensions = __import__(f"{app_}.django_settings")
            if hasattr(settings_extensions.django_settings, "SETTINGS"):
                settings = settings_extensions.django_settings.SETTINGS
                cls._validate_module_settings(settings)
                module_settings_extension = settings
                logger.debug(f"{app_} Module SETTINGS loaded.")
            else:
                logger.debug(f"{app_} has a django_settings attached but no SETTINGS variable")
        except ModuleNotFoundError as exc:
            logger.debug(f"{app_} has no django_settings, skipping")
        except AssertionError as e:
            logger.error(e)
        except Exception as exc:
            logger.debug(f"{app_}: unknown exception occurred during loading SETTINGSn: {exc}")
        finally:
            return module_settings_extension

    @classmethod
    def _validate_module_settings(cls, settings):
        assert isinstance(settings, list) and all([isinstance(next_, SettingsAttribute) for next_ in settings]),\
            "Invalid type of django_settings.SETTINGS. It should provide list of SettingsAttribute elements."


def load_settings_from_modules():
    ModulesSettingsLoader.load_settings_extensions()
