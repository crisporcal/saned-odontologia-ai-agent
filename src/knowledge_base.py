from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import DATA_DIR, PDF_DOCUMENTS
from src.models import KnowledgeBase


def get_knowledge_base() -> KnowledgeBase:
    documents = []

    for file_name, display_name in PDF_DOCUMENTS.items():
        pdf_path = DATA_DIR / file_name
        loader = PyPDFLoader(str(pdf_path))
        loaded_pages = loader.load()

        for page in loaded_pages:
            page.metadata["document_name"] = display_name
            page.metadata["source_file"] = file_name
            documents.append(page)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=950,
        chunk_overlap=180,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    return KnowledgeBase(
        chunks=chunks,
        document_names=list(PDF_DOCUMENTS.values()),
    )
