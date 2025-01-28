# ---------|| CONFIGURATION ||---------
__version__ = "0.1"
app_name = "Ashvin IDP"

import streamlit as st
from time import time as now

# Set Streamlit page configuration
st.set_page_config(layout="centered", page_title=f"{app_name} {__version__}")

# Session state initialization
ss = st.session_state
if "debug" not in ss:
    ss["debug"] = {}

# Import custom CSS
import css

st.write(f"<style>{css.v1}</style>", unsafe_allow_html=True)

# Header placeholders
header1, header2, header3 = st.empty(), st.empty(), st.empty()

# ---------|| COMPONENTS ||---------


def ui_spacer(n=2, line=False, next_n=0):
    """Adds spacing and optional line to UI."""
    for _ in range(n):
        st.write("")
    if line:
        st.tabs([" "])
    for _ in range(next_n):
        st.write("")


def ui_info():
    """Displays application information."""
    st.markdown(
        """
        # Ashvin IDP System
        """
    )


def index_pdf_file():
    """Handles PDF file indexing."""

    if ss.get("pdf_file"):
        ss["filename"] = ss["pdf_file"].name
        if ss["filename"] != ss.get("filename_done"):
            pass


# ---------|| UI COMPONENTS ||---------


def ui_pdf_file():
    """Handles PDF file upload and selection."""
    st.write("## Upload a new file")
    t1, t2 = st.tabs(["UPLOAD", "FILES"])

    with t1:
        st.file_uploader(
            "pdf file",
            type="pdf",
            key="pdf_file",
            on_change=index_pdf_file,
            label_visibility="collapsed",
        )

    with t2:
        pass


# ---------|| LAYOUT ||---------

with st.sidebar:
    ui_info()
    ui_pdf_file()


def main():
    pass


if __name__ == "__main__":
    main()
