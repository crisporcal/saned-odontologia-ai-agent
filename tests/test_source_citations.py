import unittest
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from src.agent import generate_llm_answer, generate_local_answer
from src.knowledge_base import get_knowledge_base
from src.models import RetrievedSource
from src.retriever import retrieve


class SourceCitationTests(unittest.TestCase):
    def test_pdf_page_is_converted_to_one_based_number(self):
        chunks = [Document(page_content="Limpieza dental profesional.",
                           metadata={"document_name": "Servicios", "page": 0})]
        source = retrieve("limpieza", chunks)[0]
        self.assertEqual(source.page_number, 1)
        self.assertEqual(source.citation, "Servicios (p. 1)")

    def test_missing_or_invalid_page_does_not_invent_a_reference(self):
        for page in (None, -1, "2", True):
            with self.subTest(page=page):
                chunk = Document(page_content="Limpieza dental profesional.",
                                 metadata={"document_name": "Servicios", "page": page})
                self.assertEqual(retrieve("limpieza", [chunk])[0].citation, "Servicios")

    def test_local_answer_keeps_distinct_pages_from_same_document(self):
        sources = [RetrievedSource("Servicios", "Limpieza dental.", 1.0, page)
                   for page in (1, 2, 1)]
        answer = generate_local_answer(sources)
        self.assertIn("Servicios (p. 1), Servicios (p. 2)", answer)
        self.assertEqual(answer.count("Servicios (p. 1)"), 1)

    @patch("src.agent.build_llm_client")
    def test_llm_receives_page_reference_in_context(self, build_client):
        build_client.return_value = {"client": Mock(), "mode": "test"}
        build_client.return_value["client"].invoke.return_value.content = "Respuesta"
        generate_llm_answer("limpieza", [RetrievedSource("Servicios", "Limpieza.", 1, 3)])
        messages = build_client.return_value["client"].invoke.call_args.args[0]
        self.assertIn("Fuente: Servicios (p. 3)", messages[1][1])

    def test_real_pdf_loader_preserves_page_references(self):
        knowledge_base = get_knowledge_base()
        sources = retrieve("servicios", knowledge_base.chunks)
        self.assertTrue(sources)
        self.assertTrue(all(source.page_number is not None and source.page_number >= 1
                            for source in sources))


if __name__ == "__main__":
    unittest.main()
