# ---------|| CONFIGURATION ||---------
__version__ = "0.1"
app_name = "Ashvin IDP"

import streamlit as st
import pandas as pd
from time import time as now

from main import Main

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


# ---------|| PYTHON ||---------
main_worker = Main()


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
    st.markdown(
        """
        # Ashvin IDP System
        """
    )


def ui_controls():

    if st.button("Delete session"):
        main_worker.delete_session()
        st.success("Database cleared!")

    if st.button("Rerun ML"):
        main_worker.delete_session()
        main_worker.rerun()
        # Rerun Main
        st.success("New session started!")
    pass


def index_pdf_file():
    if ss.get("pdf_file"):
        ss["filename"] = ss["pdf_file"].name
        if ss["filename"] != ss.get("filename_done"):
            pass


# ---------|| UI COMPONENTS ||---------


def ui_pdf_file():
    """Handles PDF file upload and selection."""
    st.write("## Upload a new file")
    t1, t2 = st.tabs(["UPLOAD", "QUEUE"])

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


# ---------|| ANAlYTICS ||---------
def show_clusters():

    data = main_worker.query_by_clusters()

    st.header("Document Clusters")
    cluster_ids = list(data.keys())

    if not cluster_ids or len(cluster_ids) == 0:
        st.info("No clusters available.")
        return

    cluster_ids.sort()

    chosen_cluster = st.selectbox("Choose a cluster", cluster_ids)

    st.subheader(f"Documents in Cluster {chosen_cluster}")
    docs_in_cluster = data[chosen_cluster]
    table_rows = []
    for doc in docs_in_cluster:
        table_rows.append(
            {
                "Cluster": chosen_cluster,
                "Name of File": doc.get("document_id", "N/A"),
                "Label": doc.get("label", "N/A"),
                "Pages": len(doc.get("pages", [])),
                "Extraction Method": doc.get("method", "N/A"),
                "Tables": doc.get("tables_count", "N/A"),
                "Images": doc.get("images_count", "N/A"),
            }
        )

    if table_rows:
        df = pd.DataFrame(table_rows)
        st.table(df)
    else:
        st.info("No documents in this cluster.")


# ---------|| LAYOUT ||---------

with st.sidebar:
    ui_info()
    ui_controls()
    ui_pdf_file()


def main():
    show_clusters()
    pass


if __name__ == "__main__":
    main()
