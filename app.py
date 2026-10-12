"""Streamlit entry point. HAR processing and Gemini run in the user's browser."""
from pathlib import Path

import streamlit as st

from web_bundle import build_html


def main() -> None:
    st.set_page_config(
        page_title="Extractor Facebook HAR + IA",
        page_icon="📊",
        layout="wide",
    )
    try:
        content = build_html(Path(__file__).parent)
    except (OSError, ValueError) as error:
        st.error(f"No se pudo cargar el extractor: {error}")
        st.info("Sube todos los archivos del paquete a la misma carpeta que app.py.")
        st.stop()
        return
    st.iframe(
        content,
        height="content",
        width="stretch",
        alt="Extractor Facebook: carga HAR, clasificación IA y reporte Excel",
    )


if __name__ == "__main__":
    main()
