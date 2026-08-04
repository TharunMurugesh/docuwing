from abc import abstractmethod

from docuwing_engine.domain.entities import ExtractionResult
from docuwing_engine.plugins.sdk import PluginBase


class Validator(PluginBase):
    @abstractmethod
    async def validate(self, result: ExtractionResult) -> ExtractionResult: ...
