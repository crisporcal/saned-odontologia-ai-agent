import math
import re
import unicodedata
from collections import Counter

from langchain_core.documents import Document

from src.models import RetrievedSource

STOPWORDS = {
    "ante",
    "bajo",
    "con",
    "contra",
    "del",
    "desde",
    "durante",
    "entre",
    "esta",
    "este",
    "las",
    "los",
    "mas",
    "para",
    "por",
    "que",
    "sin",
    "sobre",
    "una",
}


def retrieve(question: str, chunks: list[Document], limit: int = 4) -> list[RetrievedSource]:
    query_terms = tokenize(question)
    if not query_terms:
        return []

    document_frequency = build_document_frequency(chunks)
    total_documents = len(chunks)
    scored_chunks = []

    for chunk in chunks:
        if is_low_value_chunk(chunk.page_content):
            continue

        terms = tokenize(chunk.page_content)
        if not terms:
            continue

        term_counts = Counter(terms)
        score = score_terms(query_terms, term_counts, document_frequency, total_documents)

        if score > 0:
            scored_chunks.append(
                RetrievedSource(
                    document_name=chunk.metadata.get("document_name", "Documento"),
                    content=chunk.page_content.strip(),
                    score=score,
                )
            )

    return sorted(scored_chunks, key=lambda item: item.score, reverse=True)[:limit]


def build_document_frequency(chunks: list[Document]) -> Counter:
    document_frequency: Counter = Counter()

    for chunk in chunks:
        document_frequency.update(set(tokenize(chunk.page_content)))

    return document_frequency


def score_terms(
    query_terms: list[str],
    term_counts: Counter,
    document_frequency: Counter,
    total_documents: int,
) -> float:
    score = 0.0
    chunk_length = sum(term_counts.values()) or 1

    for term in query_terms:
        frequency = term_counts.get(term, 0)
        if frequency == 0:
            continue

        tf = frequency / chunk_length
        idf = math.log((total_documents + 1) / (document_frequency.get(term, 0) + 1)) + 1
        score += tf * idf

    return score


def tokenize(text: str) -> list[str]:
    normalized = remove_accents(text.lower())
    words = re.findall(r"[a-z0-9ñ]+", normalized)
    return [word for word in words if len(word) > 2 and word not in STOPWORDS]


def is_low_value_chunk(text: str) -> bool:
    normalized = remove_accents(text.lower())
    looks_like_index = (
        "indice" in normalized
        and "introduccion" in normalized
        and "contacto" in normalized
    )
    looks_like_cover = (
        "version" in normalized
        and "fecha de vigencia" in normalized
        and len(normalized) < 700
    )

    return looks_like_index or looks_like_cover


def remove_accents(text: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFD", text)
        if unicodedata.category(character) != "Mn"
    )
