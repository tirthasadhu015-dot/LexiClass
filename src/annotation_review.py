"""Manual, human-only annotation review for the LexiClass Parquet corpus."""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARQUET = REPO_ROOT / "dataset" / "raw" / "train-00000 (1).parquet"
DEFAULT_ANNOTATIONS = REPO_ROOT / "dataset" / "annotations" / "annotation_template.csv"
TARGET_CATEGORIES = (
    "Criminal Law",
    "Civil Law",
    "Constitutional Law",
    "Property Law",
    "Other Legal Domains",
)
REVIEW_REQUIRED = "REVIEW_REQUIRED"
REVIEW_STATUSES = ("PENDING", "ADJUDICATED", REVIEW_REQUIRED)
ANNOTATION_COLUMNS = (
    "document_id", "document_title", "category", "annotation_notes", "reviewer_status"
)
DOCUMENT_COLUMNS = (
    "doc_id", "document_title", "document_type", "document_jurisdiction",
    "issuing_authority", "text",
)


class AnnotationReviewError(ValueError):
    """Raised when annotation or source data does not meet review requirements."""


def validate_annotation_values(category: str, reviewer_status: str) -> None:
    """Validate a label/status pair without inferring or changing either value."""
    category = str(category).strip()
    reviewer_status = str(reviewer_status).strip()
    if reviewer_status not in REVIEW_STATUSES:
        raise AnnotationReviewError(f"Invalid reviewer_status: {reviewer_status!r}")
    if reviewer_status == "PENDING":
        if category:
            raise AnnotationReviewError("A PENDING annotation must have a blank category.")
        return
    if reviewer_status == REVIEW_REQUIRED:
        if category != REVIEW_REQUIRED:
            raise AnnotationReviewError("REVIEW_REQUIRED status requires REVIEW_REQUIRED category.")
        return
    if category not in TARGET_CATEGORIES:
        raise AnnotationReviewError("ADJUDICATED status requires one of the five approved categories.")


def validate_annotation_frame(frame: pd.DataFrame) -> None:
    """Validate annotation columns, status values, and category/status pairs."""
    missing = [column for column in ANNOTATION_COLUMNS if column not in frame.columns]
    if missing:
        raise AnnotationReviewError("Missing annotation column(s): " + ", ".join(missing))
    for row_number, row in frame.iterrows():
        category = "" if pd.isna(row["category"]) else str(row["category"]).strip()
        status = "" if pd.isna(row["reviewer_status"]) else str(row["reviewer_status"]).strip()
        try:
            validate_annotation_values(category, status)
        except AnnotationReviewError as error:
            raise AnnotationReviewError(f"Annotation row {row_number + 2}: {error}") from error


def read_annotations(path: str | Path) -> tuple[pd.DataFrame, str]:
    """Load and validate an annotation CSV, returning it with its content hash."""
    path = Path(path)
    try:
        raw = path.read_bytes()
        frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except (OSError, pd.errors.ParserError, UnicodeError) as error:
        raise AnnotationReviewError(f"Could not read annotation CSV: {error}") from error
    validate_annotation_frame(frame)
    return frame, hashlib.sha256(raw).hexdigest()


def next_pending_index(frame: pd.DataFrame) -> int | None:
    """Return the next PENDING row index, or None when review is complete."""
    validate_annotation_frame(frame)
    pending = frame.index[frame["reviewer_status"].astype(str).str.strip().eq("PENDING")]
    return int(pending[0]) if len(pending) else None


def load_pending_documents(parquet_path: str | Path, document_ids: Iterable[str]) -> dict[str, dict[str, str]]:
    """Read only needed document columns and retain only requested IDs in memory."""
    wanted = {str(value) for value in document_ids}
    if not wanted:
        return {}
    try:
        import pyarrow.parquet as parquet
    except ImportError as error:
        raise AnnotationReviewError("Parquet annotation requires pyarrow; install requirements.txt in the project venv.") from error
    try:
        parquet_file = parquet.ParquetFile(parquet_path)
        missing = [column for column in DOCUMENT_COLUMNS if column not in parquet_file.schema.names]
        if missing:
            raise AnnotationReviewError("Parquet is missing required column(s): " + ", ".join(missing))
        found: dict[str, dict[str, str]] = {}
        for batch in parquet_file.iter_batches(columns=list(DOCUMENT_COLUMNS), batch_size=8):
            for record in batch.to_pylist():
                document_id = "" if record.get("doc_id") is None else str(record["doc_id"])
                if document_id in wanted:
                    found[document_id] = {
                        column: "" if record.get(column) is None else str(record[column])
                        for column in DOCUMENT_COLUMNS
                    }
            if wanted.issubset(found):
                break
    except AnnotationReviewError:
        raise
    except Exception as error:
        raise AnnotationReviewError(f"Could not read the Parquet source: {error}") from error
    absent = sorted(wanted - set(found))
    if absent:
        raise AnnotationReviewError(f"Annotation IDs were not found in Parquet: {', '.join(absent[:5])}")
    return found


def atomic_save_annotations(
    frame: pd.DataFrame,
    path: str | Path,
    expected_hash: str | None = None,
) -> str:
    """Safely replace the annotation CSV, refusing concurrent external edits."""
    path = Path(path)
    validate_annotation_frame(frame)
    if expected_hash is not None:
        current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if current_hash != expected_hash:
            raise AnnotationReviewError("Annotation CSV changed during this session; refusing to overwrite newer edits.")
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8-sig", newline="", suffix=".tmp",
            prefix=f"{path.stem}_", dir=path.parent, delete=False,
        ) as temporary:
            temporary_name = temporary.name
        frame.to_csv(temporary_name, index=False, columns=list(frame.columns), encoding="utf-8-sig")
        os.replace(temporary_name, path)
        temporary_name = None
    except OSError as error:
        raise AnnotationReviewError(f"Could not safely save annotation CSV: {error}") from error
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _show_document(document: dict[str, str], input_fn: Callable[[str], str], output_fn: Callable[[str], None], page_chars: int) -> bool:
    """Display metadata and paginated full text. Return False when reviewer quits."""
    for label, key in (
        ("Document ID", "doc_id"), ("Document title", "document_title"),
        ("Document type", "document_type"), ("Jurisdiction", "document_jurisdiction"),
        ("Issuing authority", "issuing_authority"),
    ):
        output_fn(f"{label}: {document.get(key, '')}")
    text = document.get("text", "")
    if not text.strip():
        output_fn("Full document text: [EMPTY]")
        return True
    pages = [text[start:start + page_chars] for start in range(0, len(text), page_chars)]
    for page_number, page in enumerate(pages, start=1):
        output_fn(f"\n--- Document text page {page_number}/{len(pages)} ---\n{page}")
        if page_number < len(pages):
            action = input_fn("Press Enter for next page, or q to stop without saving: ").strip().casefold()
            if action == "q":
                return False
    return True


def _ask_category(input_fn: Callable[[str], str], output_fn: Callable[[str], None]) -> str | None:
    options = (*TARGET_CATEGORIES, REVIEW_REQUIRED)
    output_fn("\nSelect a category based only on your review of the document substance:")
    for number, category in enumerate(options, start=1):
        output_fn(f"  {number}. {category}")
    while True:
        choice = input_fn("Category number (or q to leave pending): ").strip().casefold()
        if choice == "q":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        output_fn("Enter a listed number or q.")


def run_review(
    parquet_path: str | Path = DEFAULT_PARQUET,
    annotation_path: str | Path = DEFAULT_ANNOTATIONS,
    page_chars: int = 4000,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> int:
    """Review pending records in order and save each human decision safely."""
    if page_chars < 500:
        raise AnnotationReviewError("page_chars must be at least 500.")
    input_fn = input if input_fn is None else input_fn
    output_fn = print if output_fn is None else output_fn
    frame, content_hash = read_annotations(annotation_path)
    pending_indices = [int(i) for i in frame.index[frame["reviewer_status"].eq("PENDING")]]
    if not pending_indices:
        output_fn("No PENDING documents remain.")
        return 0
    ids = [str(frame.at[index, "document_id"]) for index in pending_indices]
    documents = load_pending_documents(parquet_path, ids)
    for index in pending_indices:
        document_id = str(frame.at[index, "document_id"])
        document = documents[document_id]
        output_fn(f"\nPending document {index + 1} of {len(frame)}")
        if not _show_document(document, input_fn, output_fn, page_chars):
            output_fn("Review stopped; this document remains PENDING.")
            break
        category = _ask_category(input_fn, output_fn)
        if category is None:
            output_fn("Review stopped; this document remains PENDING.")
            break
        notes = input_fn("Annotation notes (include rationale/evidence; one line): ").strip()
        status = REVIEW_REQUIRED if category == REVIEW_REQUIRED else "ADJUDICATED"
        validate_annotation_values(category, status)
        frame.at[index, "category"] = category
        frame.at[index, "annotation_notes"] = notes
        frame.at[index, "reviewer_status"] = status
        content_hash = atomic_save_annotations(frame, annotation_path, expected_hash=content_hash)
        output_fn(f"Saved manual annotation for {document_id} as {status}.")
    next_index = next_pending_index(frame)
    if next_index is None:
        output_fn("No PENDING documents remain.")
    else:
        output_fn(f"Next PENDING document: {frame.at[next_index, 'document_id']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manually review pending LexiClass document annotations.")
    parser.add_argument("--parquet", type=Path, default=DEFAULT_PARQUET, help="Original Parquet corpus path")
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS, help="Annotation CSV path")
    parser.add_argument("--page-chars", type=int, default=4000, help="Characters shown per text page (minimum 500)")
    args = parser.parse_args(argv)
    try:
        return run_review(args.parquet, args.annotations, args.page_chars)
    except AnnotationReviewError as error:
        print(f"Annotation review stopped: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
