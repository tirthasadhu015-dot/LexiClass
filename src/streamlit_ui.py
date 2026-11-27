"""Streamlit interface for LexiClass AI."""

from __future__ import annotations

import hashlib
import html
import json
import logging
from pathlib import Path

import streamlit as st

from src.dataset_validation import LEGAL_CATEGORIES, load_and_validate_dataset
from src.legal_knowledge_base import (
    DEFAULT_CSV_PATH as LEGAL_REFERENCE_CSV_PATH,
    LegalKnowledgeBaseError,
    is_http_source_url,
    load_reference_csv,
    search_legal_references,
)
from src.prediction import (
    DEFAULT_MODEL_DIR,
    ModelArtifactError,
    load_model_artifacts,
    model_artifacts_available,
    predict_category_with_confidence,
)
from src.text_extraction import MAX_UPLOAD_SIZE_BYTES, DocumentExtractionError, extract_text


LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "dataset" / "legal_documents.csv"
EVALUATION_REPORT_PATH = PROJECT_ROOT / "reports" / "evaluation" / "evaluation_report.json"
PAGE_DASHBOARD = "Dashboard"
PAGE_CLASSIFY = "Classify Document"
PAGE_KNOWLEDGE_BASE = "Legal Knowledge Base"
PAGE_ABOUT = "About Project"


APP_CSS = """
<style>
:root {
  --deep-navy: #0F172A;
  --royal-blue: #2563EB;
  --light-blue: #DBEAFE;
  --white: #FFFFFF;
  --slate-gray: #64748B;
  --light-gray: #F1F5F9;
  --success-green: #16A34A;
  --warning-amber: #F59E0B;
  --error-red: #DC2626;
  --lexi-page: #F1F5F9;
  --lexi-surface: #FFFFFF;
  --lexi-surface-raised: #F8FAFC;
  --lexi-text: #0F172A;
  --lexi-muted: #475569;
  --lexi-border: #CBD5E1;
  --lexi-accent: #1D4ED8;
  --lexi-accent-soft: #DBEAFE;
  --lexi-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
  color-scheme: light;
}
.stApp { background: var(--lexi-page); color: var(--lexi-text); font-family: Inter, Roboto, sans-serif; }
[data-testid="stSidebar"] { background: var(--lexi-surface); color: var(--lexi-text); border-right: 1px solid var(--lexi-border); }
[data-testid="stHeader"] { background: var(--lexi-page); }
h1, h2, h3 { color: var(--lexi-text); letter-spacing: -0.02em; }
[data-testid="stMetric"] {
  background: var(--lexi-surface); color: var(--lexi-text);
  border: 1px solid var(--lexi-border); border-radius: 12px;
  padding: 16px 18px; box-shadow: var(--lexi-shadow);
}
[data-testid="stMetricLabel"] { color: var(--lexi-muted); }
.stButton > button[kind="primary"] {
  background: var(--royal-blue); border-color: var(--royal-blue); color: var(--white);
  border-radius: 9px; min-height: 42px; font-weight: 600;
}
.stButton > button[kind="primary"]:hover { background: #1D4ED8; border-color: #1D4ED8; }
.stButton > button { border-radius: 9px; }
.upload-panel {
  background: var(--lexi-surface); color: var(--lexi-text);
  border: 1px dashed var(--lexi-accent); border-radius: 12px;
  padding: 18px; margin: 8px 0 16px;
}
.eyebrow { color: var(--lexi-accent); font-size: 0.78rem; font-weight: 700; letter-spacing: 0.09em; }
.hero-panel {
  background: linear-gradient(120deg, var(--lexi-surface), var(--lexi-surface-raised));
  color: var(--lexi-text); border: 1px solid var(--lexi-border);
  border-radius: 16px; padding: 28px 30px; margin-bottom: 18px;
}
.hero-panel h1 { margin: 4px 0 8px; font-size: 2.1rem; }
.hero-panel p { color: var(--lexi-muted); margin-bottom: 0; }
.category-card {
  background: var(--lexi-surface); color: var(--lexi-text);
  border: 1px solid var(--lexi-border); border-radius: 12px;
  padding: 14px 16px; min-height: 74px; margin-bottom: 10px; box-shadow: var(--lexi-shadow);
}
.category-card strong { color: var(--lexi-text); }
.category-card span { display: block; color: var(--lexi-muted); font-size: 0.86rem; margin-top: 4px; }
.result-panel {
  background: var(--lexi-surface); color: var(--lexi-text);
  border: 1px solid var(--lexi-border); border-left: 5px solid var(--royal-blue);
  border-radius: 12px; padding: 18px 20px; margin: 12px 0; box-shadow: var(--lexi-shadow);
}
.small-muted { color: var(--lexi-muted); font-size: 0.88rem; }
/* Theme tokens are populated from Streamlit's active theme on each render. */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background-color: var(--lexi-page); color: var(--lexi-text);
}
[data-testid="stSidebar"] {
  background-color: var(--lexi-surface); color: var(--lexi-text);
  border-right: 1px solid var(--lexi-border);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] small { color: var(--lexi-text); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * { color: var(--lexi-muted); }
[data-testid="stSidebar"] [role="radiogroup"] label { background: transparent; }
[data-testid="stSidebar"] input[type="radio"] { accent-color: var(--lexi-accent); }
[data-testid="stHeader"] { background: var(--lexi-page); }
h1, h2, h3, h4, h5, h6, p, li, label,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] { color: var(--lexi-text); }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--lexi-muted); }
a { color: var(--lexi-accent); }
[data-testid="stMetric"] {
  background: var(--lexi-surface); color: var(--lexi-text);
  border: 1px solid var(--lexi-border); box-shadow: var(--lexi-shadow);
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"], [data-testid="stMetricValue"] *,
[data-testid="stMetricDelta"], [data-testid="stMetricDelta"] *,
[data-testid="stTooltipIcon"] { color: var(--lexi-text) !important; }
.upload-panel, .category-card, .result-panel {
  background: var(--lexi-surface); color: var(--lexi-text);
  border-color: var(--lexi-border); box-shadow: var(--lexi-shadow);
}
.result-panel { border-left-color: var(--royal-blue); }
.upload-panel { border-style: dashed; border-color: var(--lexi-accent); }
.hero-panel {
  background: linear-gradient(120deg, var(--lexi-surface), var(--lexi-surface-raised));
  color: var(--lexi-text); border-color: var(--lexi-border);
}
.hero-panel p, .category-card span, .small-muted { color: var(--lexi-muted); }
.category-card strong, .result-panel h2, .result-panel p { color: var(--lexi-text); }
.eyebrow { color: var(--lexi-accent); }
.stButton > button { color: var(--lexi-text); border-color: var(--lexi-border); }
.stButton > button:not([kind="primary"]) { background: var(--lexi-surface); }
input, textarea, [data-baseweb="select"] > div {
  background-color: var(--lexi-surface) !important; color: var(--lexi-text) !important;
  border-color: var(--lexi-border) !important;
}
input::placeholder, textarea::placeholder { color: var(--lexi-muted) !important; opacity: 0.85; }
[data-testid="stExpander"] { background: var(--lexi-surface); border-color: var(--lexi-border); }
@media (max-width: 700px) {
  .hero-panel { padding: 20px; }
  .hero-panel h1 { font-size: 1.65rem; }
}
</style>
"""


LIGHT_THEME_VARIABLES = {
    "--lexi-page": "#F1F5F9",
    "--lexi-surface": "#FFFFFF",
    "--lexi-surface-raised": "#F8FAFC",
    "--lexi-text": "#0F172A",
    "--lexi-muted": "#475569",
    "--lexi-border": "#CBD5E1",
    "--lexi-accent": "#1D4ED8",
    "--lexi-accent-soft": "#DBEAFE",
}
DARK_THEME_VARIABLES = {
    "--lexi-page": "#0B1220",
    "--lexi-surface": "#111827",
    "--lexi-surface-raised": "#1E293B",
    "--lexi-text": "#F8FAFC",
    "--lexi-muted": "#CBD5E1",
    "--lexi-border": "#475569",
    "--lexi-accent": "#93C5FD",
    "--lexi-accent-soft": "#1E3A5F",
}


def _theme_context_type() -> str | None:
    """Return Streamlit's theme type where available; context can lag or be absent."""
    try:
        value = st.context.theme.type
    except Exception:
        return None
    return value if value in {"light", "dark"} else None


def _theme_fallback_css(theme_type: str | None) -> str:
    """Set root tokens from Streamlit's active theme, defaulting to Light.

    Streamlit does not guarantee a public ``data-theme`` DOM attribute for
    custom CSS. Its theme context is the source of truth on app render; the
    explicit Light config and Light fallback cover first load and test contexts.
    """
    variables = DARK_THEME_VARIABLES if theme_type == "dark" else LIGHT_THEME_VARIABLES
    color_scheme = "dark" if theme_type == "dark" else "light"
    declarations = "\n".join(f"  {name}: {value};" for name, value in variables.items())
    shadow = "0 2px 10px rgba(0, 0, 0, 0.28)" if theme_type == "dark" else "0 2px 8px rgba(15, 23, 42, 0.06)"
    return (
        f":root {{\n{declarations}\n"
        f"  --lexi-shadow: {shadow};\n  color-scheme: {color_scheme};\n}}"
    )


@st.cache_resource(show_spinner=False)
def _cached_model_artifacts():
    """Load trusted local artifacts once per Streamlit process."""

    return load_model_artifacts(DEFAULT_MODEL_DIR)


def _inject_styles() -> None:
    """Inject styles using the active Streamlit theme, with Light as fallback."""
    fallback = _theme_fallback_css(_theme_context_type())
    styled_css = APP_CSS.replace("</style>", f"{fallback}\n</style>")
    st.markdown(styled_css, unsafe_allow_html=True)


def _dataset_summary() -> tuple[int | None, str]:
    _, report = load_and_validate_dataset(DATASET_PATH)
    if report.errors:
        return None, "Needs review"
    if report.row_count == 0:
        return 0, "No labeled records"
    return report.row_count, "Available"


def _evaluated_accuracy(model_ready: bool) -> str:
    """Return actual held-out accuracy only for the current dataset/model state."""

    if not model_ready or not EVALUATION_REPORT_PATH.is_file() or not DATASET_PATH.is_file():
        return "Unavailable"
    try:
        report = json.loads(EVALUATION_REPORT_PATH.read_text(encoding="utf-8"))
        current_hash = hashlib.sha256(DATASET_PATH.read_bytes()).hexdigest()
        if report.get("dataset_sha256") != current_hash:
            return "Unavailable"
        expected_artifacts = report.get("model_artifact_sha256", {})
        classifier_hash = hashlib.sha256((DEFAULT_MODEL_DIR / "classifier.joblib").read_bytes()).hexdigest()
        vectorizer_hash = hashlib.sha256((DEFAULT_MODEL_DIR / "tfidf_vectorizer.joblib").read_bytes()).hexdigest()
        if expected_artifacts.get("classifier") != classifier_hash or expected_artifacts.get("vectorizer") != vectorizer_hash:
            return "Unavailable"
        selected_model = report.get("selected_model")
        metrics = report.get("models", {}).get(selected_model, {})
        accuracy = metrics.get("accuracy")
        if not isinstance(accuracy, (int, float)):
            return "Unavailable"
        return f"{accuracy:.1%}"
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return "Unavailable"


def _render_sidebar(model_ready: bool) -> str:
    with st.sidebar:
        st.markdown("## LexiClass AI")
        st.caption("Smarter Legal Documents, Simplified.")
        st.divider()
        page = st.radio(
            "Navigate",
            (PAGE_DASHBOARD, PAGE_CLASSIFY, PAGE_KNOWLEDGE_BASE, PAGE_ABOUT),
            key="active_page",
        )
        st.divider()
        st.caption("SYSTEM STATUS")
        st.write("Classifier: **Artifacts available**" if model_ready else "Classifier: **Not trained**")
        st.caption("Predictions are informational and are not legal advice.")
    return page


@st.cache_data(show_spinner=False)
def _cached_legal_references(csv_path: str, modified_ns: int) -> list[dict[str, str]]:
    """Cache the separate reference CSV until its file timestamp changes."""
    del modified_ns
    return load_reference_csv(csv_path)


def _clear_legal_search() -> None:
    """Reset Legal Knowledge Base filters and results."""
    st.session_state["kb_query"] = ""
    st.session_state["kb_code_filter"] = "All codes"
    st.session_state["kb_section_filter"] = ""
    st.session_state.pop("kb_search_results", None)
    st.session_state.pop("kb_search_submitted", None)


def _render_legal_reference_result(record: dict[str, str], index: int) -> None:
    """Render one source record with clear distinction between metadata and law text."""
    heading = f"{record.get('code', '')} · {record.get('section', '')} · {record.get('title', '')}"
    with st.expander(heading, expanded=index == 0):
        st.markdown(f"**Act Code:** {record.get('code', '')}  \n**Section:** {record.get('section', '')}")
        st.markdown("**Dataset description** *(not official statutory wording)*")
        st.write(record.get("description") or "No description is available in this dataset record.")
        st.markdown("**Purpose (dataset-provided)**")
        st.write(record.get("purpose") or "Not provided in this dataset record.")
        st.markdown("**Context (dataset-provided)**")
        st.write(record.get("context") or "Not provided in this dataset record.")
        st.markdown("**Penalty information (dataset-provided; verify against source)**")
        st.write(record.get("penalty") or "Not provided in this dataset record.")
        st.markdown(f"**Source name:** {record.get('source_name') or 'Not provided'}")
        source_url = record.get("source_url", "")
        if is_http_source_url(source_url):
            st.link_button("Open source link as provided", source_url)
        else:
            st.caption("No valid HTTP(S) source link is available for this record.")


def _render_legal_knowledge_base() -> None:
    """Render searchable statutory reference data independently from ML classification."""
    st.title("Legal Knowledge Base")
    st.write("Search dataset-provided Indian legal reference entries by Act code, section, title, description, or keywords.")
    st.warning(
        "Educational legal information only, not legal advice. Descriptions and penalty fields are dataset-provided, "
        "not guaranteed official statutory wording or current law. Verify current legal status and exact text using the source link. "
        "Legacy Act references such as IPC are not automatically converted to BNS references."
    )
    if not LEGAL_REFERENCE_CSV_PATH.is_file():
        st.info("The reference index has not been generated yet.")
        st.code(".\\.venv\\Scripts\\python.exe -m src.legal_knowledge_base process", language="powershell")
        return
    try:
        with st.spinner("Loading legal reference entries..."):
            references = _cached_legal_references(
                str(LEGAL_REFERENCE_CSV_PATH), LEGAL_REFERENCE_CSV_PATH.stat().st_mtime_ns
            )
    except LegalKnowledgeBaseError:
        LOGGER.exception("Could not load the legal reference index.")
        st.error("The Legal Knowledge Base could not be loaded. Check its generated CSV and processing report.")
        return
    codes = sorted({record["code"] for record in references if record.get("code")})
    code_options = ["All codes", *codes]
    if st.session_state.get("kb_code_filter", "All codes") not in code_options:
        st.session_state["kb_code_filter"] = "All codes"
    st.caption(f"Reference records available: {len(references)}")

    with st.form("legal_knowledge_base_search"):
        query_column, code_column, section_column = st.columns([2.2, 1, 1])
        query = query_column.text_input(
            "Search title, description, or keywords", key="kb_query",
            placeholder="Enter legal term or title",
        )
        selected_code = code_column.selectbox("Act Code", code_options, key="kb_code_filter")
        section = section_column.text_input("Section", key="kb_section_filter", placeholder="e.g. 1 or Section 1")
        submitted = st.form_submit_button("Search", type="primary", use_container_width=True)
    st.button("Clear search", on_click=_clear_legal_search)

    if submitted:
        if not (query.strip() or section.strip() or selected_code != "All codes"):
            st.session_state["kb_search_results"] = []
            st.session_state["kb_search_submitted"] = True
        else:
            st.session_state["kb_search_results"] = search_legal_references(
                references,
                code="" if selected_code == "All codes" else selected_code,
                section=section,
                query=query,
                limit=100,
            )
            st.session_state["kb_search_submitted"] = True

    results = st.session_state.get("kb_search_results")
    if results is None:
        st.info("Enter a search term or choose an Act Code or section, then select Search.")
    elif not results:
        st.info("No matching legal reference entries were found. Try a different term or clear the filters.")
    else:
        st.caption(f"Matches: {len(results)}" + (" (showing the first 100)" if len(results) == 100 else ""))
        for index, record in enumerate(results):
            _render_legal_reference_result(record, index)


def _render_category_cards() -> None:
    st.subheader("Supported legal categories")
    descriptions = {
        "Criminal Law": "Criminal offences and proceedings",
        "Civil Law": "Civil disputes and legal relationships",
        "Constitutional Law": "Constitutional provisions and fundamental rights",
        "Property Law": "Land, ownership, and property disputes",
        "Other Legal Domains": "Legal topics outside the four primary categories",
    }
    columns = st.columns(2)
    for index, category in enumerate(LEGAL_CATEGORIES):
        with columns[index % 2]:
            st.markdown(
                f'<div class="category-card"><strong>{category}</strong>'
                f'<span>{descriptions[category]}</span></div>',
                unsafe_allow_html=True,
            )


def _navigate_to_classification() -> None:
    """Switch to the classification page from the dashboard action."""

    st.session_state.active_page = PAGE_CLASSIFY

def _render_dashboard(model_ready: bool) -> None:
    st.markdown(
        '<div class="hero-panel"><div class="eyebrow">LEGAL DOCUMENT CLASSIFICATION</div>'
        '<h1>Welcome to LexiClass AI</h1>'
        '<p>Intelligently organize legal documents with clear, text-based analysis.</p></div>',
        unsafe_allow_html=True,
    )

    dataset_count, dataset_status = _dataset_summary()
    metric_columns = st.columns(4)
    metric_columns[0].metric("Supported categories", str(len(LEGAL_CATEGORIES)))
    metric_columns[1].metric(
        "Labeled dataset records",
        str(dataset_count) if dataset_count is not None else "Needs review",
        help="Count of validated labeled records.",
    )
    metric_columns[2].metric("Classifier status", "Artifacts available" if model_ready else "Not trained")
    metric_columns[3].metric("Held-out accuracy", _evaluated_accuracy(model_ready))

    if dataset_status == "No labeled records":
        st.info("The dataset template is empty. Model training and classification are not available yet.")
    elif dataset_status == "Needs review":
        st.warning("The dataset needs correction before it can be used for training.")

    st.button("Classify a document", type="primary", use_container_width=True, on_click=_navigate_to_classification)

    _render_category_cards()
    st.caption("Model accuracy is shown only when a matching held-out evaluation report is available.")


def _render_classification_result(result: dict[str, object]) -> None:
    category = html.escape(str(result["category"]))
    document_name = html.escape(str(result["document_name"]))
    st.markdown(
        f'<div class="result-panel"><div class="eyebrow">CLASSIFICATION RESULT</div>'
        f'<p><strong>Document:</strong> {document_name}</p><h2>{category}</h2></div>',
        unsafe_allow_html=True,
    )
    confidence = result.get("probability")
    if isinstance(confidence, float):
        st.metric("Model probability", f"{confidence:.1%}")
        st.caption("Model probabilities may be uncalibrated and are not guarantees of correctness.")
    else:
        st.caption("This classifier does not provide a probability score.")
    st.warning("This category is an informational model output, not legal advice. Verify important results with a qualified professional.")


def _render_classifier() -> None:
    st.title("Classify a legal document")
    st.write("Upload a PDF or DOCX file. Text is extracted in memory and is not saved by this page.")
    st.markdown(
        '<div class="upload-panel"><strong>Upload your legal document</strong><br>'
        '<span class="small-muted">Supported formats: PDF and DOCX. Maximum size: 20 MiB.</span></div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=("pdf", "docx"),
        help="Files are processed in memory and are not written to an uploads folder.",
    )
    if uploaded_file is None:
        st.info("Choose a file to begin. Scanned PDFs without a text layer are not supported because OCR is not enabled.")
        return

    file_size = int(uploaded_file.size)
    display_name = Path(uploaded_file.name).name
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        st.error("This file is larger than the 20 MiB upload limit.")
        return

    file_content = uploaded_file.getvalue()
    upload_key = hashlib.sha256(uploaded_file.name.encode("utf-8") + bytes([0]) + file_content).hexdigest()
    if st.session_state.get("active_upload_key") != upload_key:
        st.session_state.active_upload_key = upload_key
        st.session_state.pop("classification_result", None)

    file_type = Path(display_name).suffix.lower().lstrip(".").upper()
    detail_columns = st.columns(3)
    detail_columns[0].metric("File name", display_name)
    detail_columns[1].metric("Format", file_type)
    detail_columns[2].metric("File size", f"{file_size / (1024 * 1024):.2f} MiB")

    try:
        with st.spinner("Extracting document text..."):
            extracted_text = extract_text(uploaded_file.name, file_content)
    except DocumentExtractionError as error:
        st.error(str(error))
        return
    except Exception:
        LOGGER.exception("Unexpected document extraction error.")
        st.error("The document could not be processed. Check that it is a valid, readable PDF or DOCX file.")
        return

    st.success("Text extracted successfully.")
    st.text_area("Extracted document text", value=extracted_text, height=320, disabled=True)

    model_ready = model_artifacts_available(DEFAULT_MODEL_DIR)
    if not model_ready:
        st.info("Classification is unavailable because a trained classifier and fitted vectorizer are not installed yet.")
    if st.button(
        "Classify document",
        type="primary",
        disabled=not model_ready,
        use_container_width=True,
    ):
        try:
            with st.spinner("Classifying document..."):
                classifier, vectorizer = _cached_model_artifacts()
                category, probability = predict_category_with_confidence(
                    extracted_text,
                    classifier=classifier,
                    vectorizer=vectorizer,
                )
            st.session_state.classification_result = {
                "document_name": display_name,
                "category": category,
                "probability": probability,
            }
        except (ModelArtifactError, ValueError):
            st.error("Classification could not be completed. Check the model artifacts and document text.")
        except Exception:
            LOGGER.exception("Unexpected document classification error.")
            st.error("Classification could not be completed. Please try again later.")

    result = st.session_state.get("classification_result")
    if isinstance(result, dict) and st.session_state.get("active_upload_key") == upload_key:
        _render_classification_result(result)


def _render_about(model_ready: bool) -> None:
    st.title("About LexiClass AI")
    st.write(
        "LexiClass AI is a legal document organization project that extracts text from PDF and DOCX files "
        "and classifies documents into broad legal domains when a trained model is available."
    )
    st.subheader("How it works")
    st.markdown(
        "1. Upload a PDF or DOCX document.\n"
        "2. Extract readable text and normalize formatting.\n"
        "3. Transform text with the fitted TF-IDF vectorizer.\n"
        "4. Apply the trained classifier and display its category."
    )
    st.subheader("Supported categories")
    st.write(" | ".join(LEGAL_CATEGORIES))
    st.subheader("Current limitations")
    if not model_ready:
        st.info("No trained model is available, so classification is disabled.")
    st.markdown(
        "- OCR for scanned PDFs is not implemented.\n"
        "- Model quality depends on the source, labels, and coverage of the training data.\n"
        "- Results are informational and must not be treated as legal advice."
    )
    st.caption("Python | Streamlit | PyPDF | python-docx | scikit-learn | TF-IDF")


def render_app() -> None:
    """Configure and render the application pages."""

    st.set_page_config(
        page_title="LexiClass AI",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    try:
        _inject_styles()
        model_ready = model_artifacts_available(DEFAULT_MODEL_DIR)
        page = _render_sidebar(model_ready)

        if page == PAGE_DASHBOARD:
            _render_dashboard(model_ready)
        elif page == PAGE_CLASSIFY:
            _render_classifier()
        elif page == PAGE_KNOWLEDGE_BASE:
            _render_legal_knowledge_base()
        else:
            _render_about(model_ready)
    except Exception:
        LOGGER.exception("Unexpected application rendering error.")
        st.error("LexiClass AI could not render this page. Please refresh and try again.")
if __name__ == "__main__":
    render_app()

