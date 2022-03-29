from dataclasses import dataclass
from enum import Enum

import typing


class SettingsAttributeConflictPolicy(Enum):
    """
    Determines behaviour on conflicts of settings attributes coming from external sources.
    MERGE_YIELD - add new or combine with an already existing variable, if it's already determined then:
        * for primitives / objects: don't perform action
        * for dictionaries: add keys (recursively), if keys are already determined then don't override them
        * for iterables: add element to iterable

    MERGE_OVERRIDE - add new or combine with an already existing variable, if it's already determined then:
        * for primitives / objects: override existing variable
        * for dictionaries: add keys (recursively), if keys are already determined then override them
        * for iterables: add element to iterable

    ENFORCE - assign variable, if it's already determined then:
        * completely override existing one with new definition, unless it's fixed

    FIX - assign variable, if it's already determined then:
        * completely existing one with new definition without combining with existing content.
        Can't be overridden. If another module attempted to override it - raise FixedSettingAttribute exception.

    ENFORCE - assign variable, if it's already determined then:
        * don't perform any action

    """
    MERGE_YIELD = 'MERGE_YIELD'
    MERGE_OVERRIDE = 'MERGE_OVERRIDE'
    ENFORCE = 'ENFORCE'
    FIX = 'FIX'
    YIELD = 'YIELD'


@dataclass
class SettingsAttribute:
    """
    Settings attributes added through module.SettingsExtension have to provide information from this dataclass.
    Attributes:
        SETTING_NAME - Name of setting attribute
        SETTING_VALUE - Value of setting
        CONFLICT_POLICY - Behaviour on multiple attribute assignments
    """
    SETTING_NAME: str
    SETTING_VALUE: 'typing.Any'
    CONFLICT_POLICY: SettingsAttributeConflictPolicy = SettingsAttributeConflictPolicy.MERGE_YIELD

    @property
    def SETTING_TYPE(self):
        return type(self.SETTING_VALUE)

    def is_fixed(self):
        return self.CONFLICT_POLICY == SettingsAttributeConflictPolicy.FIX

    def is_yielding(self):
        return self.CONFLICT_POLICY == SettingsAttributeConflictPolicy.YIELD

    def is_enforced(self):
        return self.CONFLICT_POLICY == SettingsAttributeConflictPolicy.ENFORCE

    def is_mergeable(self):
        return self.CONFLICT_POLICY in \
               (SettingsAttributeConflictPolicy.MERGE_YIELD, SettingsAttributeConflictPolicy.MERGE_OVERRIDE)


class SettingsAttributeError(AttributeError):
    pass
