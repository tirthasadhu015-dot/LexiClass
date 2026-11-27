"""Processing and search helpers for the separate Indian legal reference base.

These records are reference information only. They are never written to the
LexiClass ML training dataset and this module does not assign ML categories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_PATH = PROJECT_ROOT / "dataset" / "raw" / "indian_constitution.json"
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "dataset" / "constitution" / "processed"
DEFAULT_CSV_PATH = DEFAULT_PROCESSED_DIR / "legal_reference.csv"
DEFAULT_REPORT_PATH = DEFAULT_PROCESSED_DIR / "inspection_report.json"

REFERENCE_FIELDS = (
    "code", "section", "title", "description", "purpose", "context",
    "penalty", "keywords", "source_url", "source_name",
)
SEARCH_FIELDS = ("title", "description", "keywords", "purpose", "context", "penalty")


class LegalKnowledgeBaseError(ValueError):
    """Raised for invalid reference data or failed processing/search input."""


def _field_text(value: Any) -> str:
    """Represent a JSON scalar as text without inventing missing information."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def load_reference_json(path: str | Path = DEFAULT_SOURCE_PATH) -> list[Any]:
    """Load UTF-8 JSON and require a root array, leaving record validation to processing."""
    source = Path(path)
    try:
        with source.open("r", encoding="utf-8-sig") as stream:
            records = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LegalKnowledgeBaseError(f"Could not read legal reference JSON: {error}") from error
    if not isinstance(records, list):
        raise LegalKnowledgeBaseError("Legal reference JSON root must be a list of records.")
    return records


def _normalized_duplicate_key(record: dict[str, str]) -> tuple[str, ...]:
    """Build a stable duplicate key from the complete requested record schema."""
    return tuple(re.sub(r"\s+", " ", record[field]).strip().casefold() for field in REFERENCE_FIELDS)


def prepare_reference_records(records: Iterable[Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate, normalize and report source records without silently dropping data.

    Structurally invalid non-object records and exact duplicate records are
    excluded from the export and counted. Incomplete dictionary records stay
    in the export with empty fields, and are explicitly counted for follow-up.
    """
    source_records = list(records)
    rows: list[dict[str, str]] = []
    invalid_records = duplicate_records = incomplete_records = 0
    missing_values = Counter({field: 0 for field in REFERENCE_FIELDS})
    records_by_code: Counter[str] = Counter()
    seen: set[tuple[str, ...]] = set()
    invalid_indices: list[int] = []
    duplicate_indices: list[int] = []
    incomplete_indices: list[int] = []

    for record_index, original in enumerate(source_records):
        if not isinstance(original, dict):
            invalid_records += 1
            invalid_indices.append(record_index)
            continue
        normalized = {field: _field_text(original.get(field)) for field in REFERENCE_FIELDS}
        for field, value in normalized.items():
            if not value.strip():
                missing_values[field] += 1
        key = _normalized_duplicate_key(normalized)
        if key in seen:
            duplicate_records += 1
            duplicate_indices.append(record_index)
            continue
        seen.add(key)
        missing_record_fields = [field for field, value in normalized.items() if not value.strip()]
        if missing_record_fields:
            incomplete_records += 1
            incomplete_indices.append(record_index)
        rows.append(normalized)
        records_by_code[normalized["code"].strip() or "(missing)"] += 1

    frame = pd.DataFrame(rows, columns=REFERENCE_FIELDS)
    report: dict[str, Any] = {
        "total_input_records": len(source_records),
        "successfully_processed_records": len(frame),
        "invalid_records": invalid_records,
        "duplicate_records": duplicate_records,
        "skipped_records": invalid_records + duplicate_records,
        "incomplete_records": incomplete_records,
        "missing_values_by_field": {field: int(missing_values[field]) for field in REFERENCE_FIELDS},
        "records_grouped_by_code": dict(sorted(records_by_code.items(), key=lambda item: item[0].casefold())),
        "invalid_record_indices_zero_based": invalid_indices,
        "duplicate_record_indices_zero_based": duplicate_indices,
        "incomplete_record_indices_zero_based": incomplete_indices,
        "processing_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    return frame, report


def _atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write one generated artifact via a same-directory temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding=encoding, newline="", suffix=".tmp",
            prefix=f"{path.stem}_", dir=path.parent, delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def process_reference_json(
    source_path: str | Path = DEFAULT_SOURCE_PATH,
    csv_path: str | Path = DEFAULT_CSV_PATH,
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    """Create a deterministic-schema UTF-8 CSV and actual processing report."""
    source = Path(source_path).resolve()
    output = Path(csv_path).resolve()
    report_output = Path(report_path).resolve()
    if source in (output, report_output):
        raise LegalKnowledgeBaseError("Generated output paths must not overwrite the original JSON source.")
    records = load_reference_json(source)
    frame, report = prepare_reference_records(records)
    report["output_csv"] = str(output)
    report["output_report"] = str(report_output)
    csv_content = frame.to_csv(index=False, columns=list(REFERENCE_FIELDS), lineterminator="\n")
    _atomic_write_text(output, csv_content, encoding="utf-8-sig")
    report_output.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(report_output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def load_reference_csv(path: str | Path = DEFAULT_CSV_PATH) -> list[dict[str, str]]:
    """Load the generated CSV and validate its reference schema."""
    try:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except (OSError, UnicodeError, pd.errors.ParserError) as error:
        raise LegalKnowledgeBaseError(f"Could not load legal reference CSV: {error}") from error
    missing_columns = [field for field in REFERENCE_FIELDS if field not in frame.columns]
    if missing_columns:
        raise LegalKnowledgeBaseError("Reference CSV is missing columns: " + ", ".join(missing_columns))
    return frame.loc[:, list(REFERENCE_FIELDS)].to_dict(orient="records")


def _normalise_match_text(value: Any) -> str:
    return re.sub(r"\s+", " ", _field_text(value)).strip().casefold()


def _normalise_section(value: str) -> str:
    section = _normalise_match_text(value)
    section = re.sub(r"^(section|sec\.?|article|art\.?)\s*", "", section)
    return section.strip(" .:-")


def search_legal_references(
    records: Iterable[dict[str, Any]],
    *,
    code: str = "",
    section: str = "",
    query: str = "",
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Filter records by exact code/section and substring query across text fields.

    At least one filter is required, which prevents accidental rendering of the
    entire corpus. Combined filters are joined with AND; query matches title,
    description, keywords, purpose, context, or penalty.
    """
    code_filter = _normalise_match_text(code)
    section_filter = _normalise_section(section) if section.strip() else ""
    query_filter = _normalise_match_text(query)
    if not (code_filter or section_filter or query_filter):
        return []
    results: list[dict[str, Any]] = []
    for record in records:
        if code_filter and _normalise_match_text(record.get("code")) != code_filter:
            continue
        if section_filter and _normalise_section(_field_text(record.get("section"))) != section_filter:
            continue
        searchable_text = " ".join(_field_text(record.get(field)) for field in SEARCH_FIELDS)
        if query_filter and query_filter not in _normalise_match_text(searchable_text):
            continue
        results.append(dict(record))
        if limit is not None and len(results) >= limit:
            break
    return results


def is_http_source_url(value: str) -> bool:
    """Return whether a source-provided URL is safe to render as a web link."""
    parsed = urlsplit(value.strip())
    return parsed.scheme.casefold() in {"http", "https"} and bool(parsed.netloc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process the separate LexiClass legal reference dataset.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    process = subparsers.add_parser("process", help="Validate source JSON and generate CSV/report.")
    process.add_argument("--input", type=Path, default=DEFAULT_SOURCE_PATH)
    process.add_argument("--output", type=Path, default=DEFAULT_CSV_PATH)
    process.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)
    try:
        report = process_reference_json(args.input, args.output, args.report)
    except LegalKnowledgeBaseError as error:
        parser.exit(1, f"Processing stopped: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
