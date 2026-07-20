from dataclasses import dataclass

from langchain_core.documents import Document


@dataclass(frozen=True)
class RetrievedSource:
    document_name: str
    content: str
    score: float


@dataclass(frozen=True)
class AgentAnswer:
    answer: str
    sources: list[RetrievedSource]
    mode: str


@dataclass(frozen=True)
class KnowledgeBase:
    chunks: list[Document]
    document_names: list[str]

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)
