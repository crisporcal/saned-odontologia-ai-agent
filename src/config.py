from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

PDF_DOCUMENTS = {
    "faq.pdf": "Preguntas Frecuentes",
    "politica_privacidad.pdf": "Politica de privacidad de datos del paciente",
    "politica_cancelaciones.pdf": "Politica de cancelaciones y reagendamiento",
    "guia_servicios.pdf": "Guia de servicios",
    "guia_cuidados.pdf": "Guia de Cuidados Pre y Post Tratamiento",
}
