from abc import abstractmethod

from docuwing_engine.knowledge.domain import Entity
from docuwing_engine.plugins.sdk import PluginBase


class EntityResolver(PluginBase):
    @abstractmethod
    def resolve(self, candidate: Entity, existing: list[Entity]) -> Entity: ...
