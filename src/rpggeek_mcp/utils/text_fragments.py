from __future__ import annotations

import inspect
from enum import StrEnum
from typing import Any

import jinja2

from ..resources import ResourceDirectory, read_resource_text


class FragmentID(StrEnum):
    """Identifiers for text fragment files stored in the fragments directory."""

    DEFAULT_SETTINGS = "default_settings.yaml"
    NONE = "none.md"


_environment: jinja2.Environment = jinja2.Environment()
_loaded_templates: dict[FragmentID, jinja2.Template] = {}


def _object_to_context_dict(
    obj: Any,
    *,
    include_private: bool = False,
    include_none: bool = True,
    include_properties: bool = True,
    include_fields: bool = True,
    ignore_errors: bool = True,
) -> dict[str, Any]:
    """
    Return a dictionary of an object's instance fields and @property values.

    Useful for passing rich Python objects into Jinja templates while exposing
    a predictable dictionary shape.

    Args:
        obj:
            The object to inspect.

        include_private:
            If False, skips names beginning with "_".

        include_none:
            If False, skips values that are None.

        include_properties:
            If True, includes values exposed through @property descriptors.

        include_fields:
            If True, includes normal instance attributes from obj.__dict__.

        ignore_errors:
            If True, properties that raise exceptions are skipped.
            If False, the exception is raised.

    Returns:
        A dictionary mapping attribute/property names to values.
    """

    result: dict[str, Any] = {}

    def should_include_name(name: str) -> bool:
        if not include_private and name.startswith("_"):
            return False
        return True

    def should_include_value(value: Any) -> bool:
        if not include_none and value is None:
            return False
        if callable(value):
            return False
        return True

    # Include normal instance fields, e.g. self.foo = "bar"
    if include_fields and hasattr(obj, "__dict__"):
        for name, value in vars(obj).items():
            if should_include_name(name) and should_include_value(value):
                result[name] = value

    # Include @property values defined on the class or parent classes
    if include_properties:
        for name, member in inspect.getmembers(type(obj)):
            if not isinstance(member, property):
                continue

            if not should_include_name(name):
                continue

            try:
                value = getattr(obj, name)
            except Exception:
                if ignore_errors:
                    continue
                raise

            if should_include_value(value):
                result[name] = value

    return result


def get_fragment(fragment_id: FragmentID) -> str:
    """Read and return the text content of the specified fragment file."""
    return read_resource_text(ResourceDirectory.FRAGMENTS, fragment_id)


def get_templated_fragment(fragment_id: FragmentID, context_object: Any) -> str:
    global _loaded_templates
    if fragment_id not in _loaded_templates:
        _loaded_templates[fragment_id] = _environment.from_string(
            get_fragment(fragment_id)
        )
    template: jinja2.Template = _loaded_templates[fragment_id]
    context: dict[str, Any] = _object_to_context_dict(context_object)
    result: str = template.render(context)
    return result
