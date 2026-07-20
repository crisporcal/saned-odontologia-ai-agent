import streamlit as st

from src.agent import answer_question
from src.knowledge_base import get_knowledge_base


st.set_page_config(
    page_title="SANED Odontologia AI Agent",
    page_icon="SANED",
    layout="wide",
)


@st.cache_resource(show_spinner="Procesando documentos PDF...")
def load_agent_data():
    return get_knowledge_base()


knowledge_base = load_agent_data()

st.title("SANED Odontologia AI Agent")
st.caption("Asistente RAG para el Challenge Alura Agente")

with st.sidebar:
    st.header("Base documental")
    st.write("El agente responde usando estos PDFs:")
    for document_name in knowledge_base.document_names:
        st.markdown(f"- {document_name}")

    st.divider()
    st.metric("Fragmentos indexados", knowledge_base.total_chunks)
    st.info(
        "Las respuestas son informativas y no reemplazan la evaluacion de un profesional odontologico."
    )

examples = [
    "Que servicios ofrece SANED Odontologia?",
    "Como puedo reagendar una cita?",
    "Que cuidados debo tener despues de una extraccion?",
    "Como protegen mis datos personales?",
]

selected_example = st.selectbox(
    "Puedes probar con una pregunta de ejemplo:",
    [""] + examples,
)

question = st.text_area(
    "Pregunta del paciente",
    value=selected_example,
    placeholder="Ejemplo: Que cuidados debo tener despues de una extraccion?",
    height=110,
)

if st.button("Preguntar al agente", type="primary"):
    if not question.strip():
        st.warning("Escribe una pregunta para consultar la base documental.")
    else:
        with st.spinner("Buscando informacion relevante..."):
            result = answer_question(question, knowledge_base)

        st.subheader("Respuesta")
        st.write(result.answer)

        if result.sources:
            st.subheader("Fuentes consultadas")
            for source in result.sources:
                with st.expander(f"{source.document_name} | relevancia {source.score:.2f}"):
                    st.write(source.content)

        st.caption(f"Modo de respuesta: {result.mode}")
