from abc import abstractmethod

from docuwing_engine.plugins.sdk import PluginBase


class RAGEngine(PluginBase):
    @abstractmethod
    async def query(self, question: str, workspace: str, document_id: str): ...
