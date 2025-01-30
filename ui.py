# ---------|| CONFIGURATION ||---------
__version__ = "0.1"
app_name = "Ashvin IDP"

import json
import streamlit as st
import pandas as pd
from time import time as now
import altair as alt

from main import Main

st.set_page_config(layout="centered", page_title=f"{app_name} {__version__}")

ss = st.session_state
if "debug" not in ss:
    ss["debug"] = {}

import css

st.write(f"<style>{css.v1}</style>", unsafe_allow_html=True)

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
            temp_path = f"/tmp/{ss['filename']}"
            with open(temp_path, "wb") as f:
                f.write(ss["pdf_file"].getbuffer())

            main_worker.submit_pdf(temp_path)


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
        data = show_files_queues()
        if not data:
            st.info("No files in the queue.")
            return

        st.write("### Files in the queue")
        for item in data:
            st.write(f"File: {item['file']} - Status: {item['status']}")
        pass


# ---------|| ANAlYTICS ||---------
def show_files_queues():

    with open("queue.json", "r") as f:
        queue = json.load(f)

    return queue


def show_clusters():

    data = main_worker.query_by_clusters()
    cluster_ids = list(data.keys())

    total_docs = 0
    for _, docs in data.items():
        total_docs += len(docs)

    st.header("Document Clusters")

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

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Documents", total_docs)
        st.metric("Number of Clusters", len(data.keys()))

    with col2:
        st.text("Cluster Distribution")
        counts_df = pd.DataFrame(
            [{"label": v[0]["label"], "count": len(v)} for k, v in data.items()]
        )
        counts_df.columns = ["label", "count"]
        chart = (
            alt.Chart(counts_df)
            .mark_arc()
            .encode(
                theta="count",
                color=alt.Color("label", legend=None),
                tooltip=["label", "count"],
            )
        )
        st.altair_chart(chart, use_container_width=True)


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
