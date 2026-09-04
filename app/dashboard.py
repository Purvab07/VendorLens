import sys
import os
import tempfile
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.embed import add_documents_any, get_collections
from src.gap_coverage import run_gap_analysis
from src.contradiction_check import run_contradiction_check
from src.models import is_flagged

st.set_page_config(page_title="Vendor Risk Checker", page_icon="🛡️", layout="wide")


def save_uploaded_file(uploaded_file) -> str:
    """Writes an uploaded file to a temp path on disk and returns that path."""
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name


def clear_collection(name: str):
    """Deletes all existing chunks in a collection, so re-uploads don't mix with old data."""
    collection = get_collections(name)
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])


# --- Sidebar: upload + controls ---
with st.sidebar:
    st.title("🛡️ Vendor Risk Checker")
    st.caption("Upload documents or paste a Google Doc link, then run the analysis.")

    st.divider()

    vendor_name = st.text_input("Vendor name", value="vendor_a", help="Used to label this vendor's collection")

    st.markdown("**Regulation source**")
    reg_input_type = st.radio(
        "Regulation input type",
        ["Upload file (.txt/.pdf)", "Google Doc link"],
        key="reg_type",
        label_visibility="collapsed"
    )
    regulation_files = None
    regulation_gdoc_url = None
    if reg_input_type == "Upload file (.txt/.pdf)":
        regulation_files = st.file_uploader(
            "Upload regulation file(s)",
            type=["txt", "pdf"],
            accept_multiple_files=True,
            key="reg_files"
        )
    else:
        regulation_gdoc_url = st.text_input(
            "Google Doc share link",
            key="reg_gdoc",
            help="Doc must be shared as 'Anyone with the link can view'"
        )

    st.markdown("**Vendor document source**")
    vendor_input_type = st.radio(
        "Vendor input type",
        ["Upload file (.txt/.pdf)", "Google Doc link"],
        key="vendor_type",
        label_visibility="collapsed"
    )
    vendor_files = None
    vendor_gdoc_url = None
    if vendor_input_type == "Upload file (.txt/.pdf)":
        vendor_files = st.file_uploader(
            "Upload vendor document(s)",
            type=["txt", "pdf"],
            accept_multiple_files=True,
            key="vendor_files"
        )
    else:
        vendor_gdoc_url = st.text_input(
            "Google Doc share link",
            key="vendor_gdoc",
            help="Doc must be shared as 'Anyone with the link can view'"
        )

    st.divider()
    run_button = st.button("▶ Upload & Run analysis", type="primary", use_container_width=True)
    st.caption("Runs locally via Ollama — no data leaves your machine.")


# --- Main area ---
if "results" not in st.session_state:
    st.session_state.results = None

if run_button:
    vendor_collection = vendor_name
    regulation_collection = f"{vendor_name}_regulations"

    has_regulation_source = bool(regulation_files) or bool(regulation_gdoc_url)
    has_vendor_source = bool(vendor_files) or bool(vendor_gdoc_url)

    if not has_regulation_source:
        st.error("Please provide a regulation file or Google Doc link.")
    elif not has_vendor_source:
        st.error("Please provide a vendor document or Google Doc link.")
    else:
        clear_collection(vendor_collection)
        clear_collection(regulation_collection)

        progress = st.progress(0, text="Loading documents...")

        try:
            # --- Regulation source ---
            if regulation_files:
                for f in regulation_files:
                    path = save_uploaded_file(f)
                    ext = "pdf" if f.name.lower().endswith(".pdf") else "txt"
                    add_documents_any(
                        source=path, source_type=ext,
                        source_label=f.name, collection_name=regulation_collection
                    )
            else:
                add_documents_any(
                    source=regulation_gdoc_url, source_type="gdoc",
                    source_label="regulation_gdoc", collection_name=regulation_collection
                )

            # --- Vendor source ---
            if vendor_files:
                for f in vendor_files:
                    path = save_uploaded_file(f)
                    ext = "pdf" if f.name.lower().endswith(".pdf") else "txt"
                    add_documents_any(
                        source=path, source_type=ext,
                        source_label=f.name, collection_name=vendor_collection
                    )
            else:
                add_documents_any(
                    source=vendor_gdoc_url, source_type="gdoc",
                    source_label="vendor_gdoc", collection_name=vendor_collection
                )

            progress.progress(50, text="Checking regulatory gaps...")
            gap_findings = run_gap_analysis(
                vendor_collection_name=vendor_collection,
                regulation_collection_name=regulation_collection
            )

            progress.progress(80, text="Checking for contradictions...")
            contradiction_findings = run_contradiction_check(vendor_collection_name=vendor_collection)

            progress.progress(100, text="Done.")
            progress.empty()

            st.session_state.results = {
                "gap": gap_findings,
                "contradiction": contradiction_findings,
                "vendor": vendor_collection
            }

        except Exception as e:
            progress.empty()
            st.error(f"Something went wrong: {e}")

if st.session_state.results is None:
    # --- Landing page content, shown before any analysis has been run ---
    st.markdown("## 🛡️ Check a vendor's paperwork automatically")
    st.markdown(
        "Upload a vendor's documents and the regulations they need to follow. "
        "This tool checks two things: does the vendor's paperwork actually satisfy the law, "
        "and do the vendor's own documents agree with each other."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 1️⃣ Provide documents")
        st.write("Upload files or paste Google Doc links for the regulation and the vendor's paperwork.")
    with col2:
        st.markdown("### 2️⃣ Run the analysis")
        st.write("The tool reads both, compares them by meaning, and checks for gaps and contradictions.")
    with col3:
        st.markdown("### 3️⃣ Review the findings")
        st.write("Every flag comes with the exact source text it's based on — no unexplained verdicts.")

    st.divider()

    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        st.markdown("#### 📋 Gap Coverage checks")
        st.caption("Does the vendor's paperwork actually satisfy the regulation?")
        st.markdown(
            "*Example: a regulation requires responding to complaints within 15 days, "
            "but the vendor's contract only promises to forward complaints within 5 days "
            "— with no mention of a final resolution timeline.*"
        )
    with ex_col2:
        st.markdown("#### 🔍 Contradiction checks")
        st.caption("Do the vendor's own documents agree with each other?")
        st.markdown(
            "*Example: the contract promises full encryption of customer data, "
            "but the privacy policy admits data is sometimes cached unencrypted.*"
        )

    st.divider()
    st.info("👈 Provide your documents in the sidebar, then click **Upload & Run analysis** to get started.")

else:
    # --- Results view, shown after an analysis has run ---
    gap_findings = st.session_state.results["gap"]
    contradiction_findings = st.session_state.results["contradiction"]
    vendor = st.session_state.results["vendor"]

    gap_issues = sum(is_flagged(f) for f in gap_findings)
    contradiction_issues = sum(is_flagged(f) for f in contradiction_findings)
    total_checks = len(gap_findings) + len(contradiction_findings)
    total_issues = gap_issues + contradiction_issues

    st.subheader(f"Results for `{vendor}`")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total checks run", total_checks)
    col2.metric("Regulatory gaps", gap_issues)
    col3.metric("Contradictions", contradiction_issues)
    col4.metric("Overall status", "⚠️ Issues found" if total_issues else "✅ Clean")

    st.divider()

    tab1, tab2 = st.tabs([
        f"📋 Gap Coverage ({len(gap_findings)})",
        f"🔍 Contradictions ({len(contradiction_findings)})"
    ])

    with tab1:
        if not gap_findings:
            st.write("No regulation chunks were found to check.")
        for i, flag in enumerate(gap_findings, start=1):
            badge = ":red[● Gap Found]" if is_flagged(flag) else ":green[● Satisfied]"
            with st.container(border=True):
                st.markdown(f"**Requirement {i}** — {badge}")
                left, right = st.columns(2)
                with left:
                    st.markdown("**Regulation**")
                    st.caption(flag.text_a)
                with right:
                    st.markdown("**Vendor excerpt**")
                    st.caption(flag.text_b)
                st.markdown(f"💬 {flag.explanation}")

    with tab2:
        if not contradiction_findings:
            st.write("Not enough documents to compare (need at least 2).")
        for i, flag in enumerate(contradiction_findings, start=1):
            badge = ":red[● Contradiction Found]" if is_flagged(flag) else ":green[● Consistent]"
            with st.container(border=True):
                st.markdown(f"**{flag.source_a} vs {flag.source_b}** — {badge}")
                left, right = st.columns(2)
                with left:
                    st.markdown(f"**{flag.source_a}**")
                    st.caption(flag.text_a)
                with right:
                    st.markdown(f"**{flag.source_b}**")
                    st.caption(flag.text_b)
                st.markdown(f"💬 {flag.explanation}")

    st.divider()
    if st.button("🔄 Start a new analysis"):
        st.session_state.results = None
        st.rerun()