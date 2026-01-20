"""Base models shared across Pylon API entities.

This module contains foundational models that are used by multiple
other models throughout the SDK.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PylonReference(BaseModel):
    """Reference to another Pylon entity (just ID).

    Many Pylon API responses include references to related entities
    as simple objects containing just an ID. This model represents
    those references.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
    )

    id: str = Field(description="The ID of the referenced entity")


class PylonCustomFieldValue(BaseModel):
    """Custom field value structure used by Pylon.

    In API responses, `custom_fields` are represented as an object keyed by
    slug, where each value includes at least a `value` and, for multi-select
    fields, `values`. Some APIs also repeat the slug inside the value
    payload, so we capture that here when present.

    Attributes:
        slug: The custom field slug (optional, may be included in payload).
        value: The primary value of the custom field.
        values: For multi-select fields, a list of selected values.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    slug: str | None = Field(default=None, description="The custom field slug")
    value: str = Field(default="", description="The custom field value")
    values: list[str] | None = Field(
        default=None,
        description="For multi-select fields, the list of selected values",
    )
