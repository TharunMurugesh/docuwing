from abc import abstractmethod

from docuwing_engine.domain.entities import ExtractionResult, Schema
from docuwing_engine.ir.types import DocumentIR
from docuwing_engine.plugins.sdk import PluginBase


class Extractor(PluginBase):
    @abstractmethod
    async def extract(self, ir: DocumentIR, schema: Schema) -> ExtractionResult: ...
