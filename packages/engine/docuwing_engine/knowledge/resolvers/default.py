from __future__ import annotations

import re

from docuwing_engine.interfaces.entity_resolver import EntityResolver
from docuwing_engine.knowledge.domain import Entity
from docuwing_engine.plugins.registry import PluginCategory, PluginManifest


class DefaultEntityResolver(EntityResolver):
    """Deterministic resolver; embedding similarity may be layered in later."""

    MANIFEST = PluginManifest(name="default_entity_resolver", category=PluginCategory.ENTITY_RESOLVER)

    @staticmethod
    def _normalise(value: str) -> str:
        return re.sub(r"\W+", "", value).lower()

    def resolve(self, candidate: Entity, existing: list[Entity]) -> Entity:
        key = self._normalise(candidate.name)
        for entity in existing:
            if entity.type == candidate.type and self._normalise(entity.name) == key:
                entity.attributes.update(candidate.attributes)
                return entity
        return candidate
