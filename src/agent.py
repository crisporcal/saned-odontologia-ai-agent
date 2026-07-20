import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.models import AgentAnswer, KnowledgeBase, RetrievedSource
from src.retriever import retrieve

load_dotenv()


def answer_question(question: str, knowledge_base: KnowledgeBase) -> AgentAnswer:
    clean_question = question.strip()

    if not clean_question:
        return AgentAnswer(
            answer="Escribe una pregunta para que pueda ayudarte con la informacion de SANED Odontologia.",
            sources=[],
            mode="validacion",
        )

    sources = retrieve(clean_question, knowledge_base.chunks)

    if not sources:
        return AgentAnswer(
            answer=(
                "No encontre informacion suficiente en los documentos cargados para responder con seguridad. "
                "Te recomiendo contactar directamente a SANED Odontologia para confirmar este punto."
            ),
            sources=[],
            mode="sin contexto",
        )

    llm_answer, llm_mode = generate_llm_answer(clean_question, sources)

    return AgentAnswer(
        answer=llm_answer or generate_local_answer(sources),
        sources=sources,
        mode=llm_mode if llm_answer else "local",
    )


def generate_llm_answer(question: str, sources: list[RetrievedSource]) -> tuple[str | None, str]:
    llm = build_llm_client()
    if llm is None:
        return None, "local"

    context = "\n\n".join(
        f"Fuente: {source.document_name}\n{source.content}" for source in sources
    )

    try:
        response = llm["client"].invoke(
            [
                (
                    "system",
                    "Eres el asistente virtual de SANED Odontologia. Responde en espanol claro, amable y breve. "
                    "Usa solo el contexto entregado. Si la informacion no esta en el contexto, dilo. "
                    "No diagnostiques ni reemplaces la consulta odontologica profesional.",
                ),
                (
                    "human",
                    f"Pregunta del paciente: {question}\n\nContexto documental:\n{context}",
                ),
            ]
        )
    except Exception as error:
        print(f"No se pudo usar el proveedor LLM configurado: {error}")
        return None, "local"

    return response.content.strip(), llm["mode"]


def build_llm_client() -> dict[str, ChatOpenAI | str] | None:
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
        return {
            "client": ChatOpenAI(
                model=model,
                temperature=0.2,
                api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/",
                    "X-Title": "SANED Odontologia AI Agent",
                },
            ),
            "mode": f"OpenRouter ({model})",
        }

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return {
            "client": ChatOpenAI(model=model, temperature=0.2, api_key=openai_api_key),
            "mode": f"ChatGPT ({model})",
        }

    return None


def generate_local_answer(sources: list[RetrievedSource]) -> str:
    best_source = sources[0]
    source_names = ", ".join(sorted({source.document_name for source in sources}))
    summary = summarize_text(best_source.content)

    return (
        "Segun la documentacion disponible de SANED Odontologia:\n\n"
        f"{summary}\n\n"
        f"Fuentes consultadas: {source_names}.\n\n"
        "Esta respuesta es informativa y no reemplaza la orientacion directa del profesional odontologico."
    )


def summarize_text(text: str) -> str:
    sentences = [
        sentence.strip()
        for sentence in text.replace("\n", " ").split(".")
        if sentence.strip()
    ]
    selected = sentences[:4]
    if not selected:
        return text[:700]

    return ". ".join(selected) + "."
