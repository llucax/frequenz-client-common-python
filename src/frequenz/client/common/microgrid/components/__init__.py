# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Provide the deprecated component ID compatibility import."""

from typing import final

from frequenz.core.id import BaseId
from typing_extensions import deprecated


@deprecated(
    "frequenz.client.common.microgrid.components.ComponentId is deprecated "
    "since v0.4.1. Use [frequenz.client.common.microgrid."
    "electrical_components.ElectricalComponentId][] instead."
)
@final
class ComponentId(BaseId, str_prefix="CID"):
    """A unique identifier for a microgrid component."""


__all__ = ["ComponentId"]
