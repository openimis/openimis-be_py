import logging
from typing import Protocol
from .settings_attributes import SettingsAttribute, SettingsAttributeError, SettingsAttributeConflictPolicy


logger = logging.getLogger(__name__)


class SettingsAttributeConflictResolveStrategy(Protocol):
    def is_strategy_matching(self, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute) -> bool:
        ...

    def resolve_conflict(self, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute) \
            -> SettingsAttribute:
        ...


class _AssignIfEmpty(SettingsAttributeConflictResolveStrategy):
    def is_strategy_matching(self, existing_attribute, new_attribute):
        return existing_attribute is None

    def resolve_conflict(self, existing_attribute, new_attribute):
        return new_attribute


class _SkipIfYielding(SettingsAttributeConflictResolveStrategy):
    def is_strategy_matching(self, existing_attribute, new_attribute):
        return new_attribute.is_yielding()

    def resolve_conflict(self, existing_attribute, new_attribute):
        return existing_attribute


class _RaiseExceptionOnFixed(SettingsAttributeConflictResolveStrategy):
    def is_strategy_matching(self, existing_attribute, new_attribute):
        return existing_attribute.is_fixed()

    def resolve_conflict(self, existing_attribute, new_attribute):
        self._raise_fixed_override_exception(new_attribute)

    @classmethod
    def _raise_fixed_override_exception(cls, current):
        raise SettingsAttributeError(F"Immutable SETTINGS attribute {current.SETTING_NAME} can't be modified.")


class _EnforceNewValue(SettingsAttributeConflictResolveStrategy):
    def is_strategy_matching(self, existing_attribute, new_attribute):
        return new_attribute.is_enforced()

    def resolve_conflict(self, existing_attribute, new_attribute):
        return new_attribute


class _MergeAttributes(SettingsAttributeConflictResolveStrategy):
    def is_strategy_matching(self, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute) -> bool:
        return existing_attribute and new_attribute.is_mergeable()

    def resolve_conflict(self, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute) \
            -> SettingsAttribute:
        return self._merge_settings(existing_attribute, new_attribute)

    @classmethod
    def _merge_settings(cls, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute):
        types_ = (existing_attribute.SETTING_TYPE, new_attribute.SETTING_TYPE)
        if types_ == (dict, dict):
            return cls._merge_recursively(existing_attribute, new_attribute)
        elif types_ == (list, list):
            return cls._combine_lists(existing_attribute, new_attribute)
        elif types_ == (list, str):
            return cls._append_to_list(existing_attribute, new_attribute)
        else:
            replace_primitive = new_attribute.CONFLICT_POLICY == SettingsAttributeConflictPolicy.MERGE_OVERRIDE
            logger.warning(F"Attributes of types {types_} cannot be merged."
                           F"Value of `{existing_attribute.SETTING_NAME}` setting attribute will "
                           F"{'not ' if not replace_primitive else ''}"
                           F"be replaced with incoming value.")
            new_attribute.SETTING_VALUE = \
                new_attribute.SETTING_VALUE if replace_primitive else existing_attribute.SETTING_VALUE
            return new_attribute

    @classmethod
    def _merge_recursively(cls, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute):
        new_value = cls._merge_dictionaries(
            existing_attribute.SETTING_VALUE, new_attribute.SETTING_VALUE, new_attribute.CONFLICT_POLICY)
        new_attribute.SETTING_VALUE = new_value
        return new_attribute

    @classmethod
    def _combine_lists(cls, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute):
        to_add = new_attribute.SETTING_VALUE
        current_setting = existing_attribute.SETTING_VALUE
        new_value = cls._add_to_list(current_setting, to_add)
        new_attribute.SETTING_VALUE = new_value
        return new_attribute

    @classmethod
    def _append_to_list(cls, existing_attribute: SettingsAttribute, new_attribute: SettingsAttribute):
        if new_attribute.SETTING_VALUE not in existing_attribute:
            new_attribute.SETTING_VALUE = [*existing_attribute.SETTING_VALUE, new_attribute.SETTING_VALUE]
        else:
            new_attribute.SETTING_VALUE = existing_attribute.SETTING_VALUE
        return new_attribute

    @classmethod
    def _merge_dictionaries(cls, existing_dict, new_dict, conflict_policy):
        def _is_node_dict(first, second):
            return isinstance(first, dict) and isinstance(second, dict)

        def _set_non_dict_value(dict_, value_, key_):
            current_value = dict_.get(key_)
            if isinstance(current_value, list) and isinstance(value_, list):
                dict_[key_] = cls._add_to_list(current_value, value_)
            elif current_value and conflict_policy == SettingsAttributeConflictPolicy.MERGE_YIELD:
                pass
            elif not current_value or conflict_policy == SettingsAttributeConflictPolicy.MERGE_OVERRIDE:
                dict_[key_] = value_

        for key in new_dict.keys():
            current_node, new_node = existing_dict.get(key), new_dict.get(key)
            if new_node:
                if _is_node_dict(current_node, new_node):
                    cls._merge_dictionaries(current_node, new_node, conflict_policy)
                else:
                    _set_non_dict_value(existing_dict, new_node, key)
            else:
                existing_dict[key] = new_node

        return existing_dict

    @classmethod
    def _add_to_list(cls, current_setting: list, to_add: list):
        for element in to_add:
            if element not in current_setting:
                current_setting.append(element)
        return current_setting


REGISTERED_STRATEGIES = [
    _AssignIfEmpty(),
    _SkipIfYielding(),
    _RaiseExceptionOnFixed(),
    _EnforceNewValue(),
    _MergeAttributes()
]
