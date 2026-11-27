"""Inspect and import licensed CSV/JSON/Parquet corpora into staging.

The importer never infers legal categories. Only exact, explicitly configured
source-label mappings with a documented human validation basis are applied.
Original source fields are retained as JSON in ``original_metadata``.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from src.dataset_validation import LEGAL_CATEGORIES, MIN_DOCUMENT_TEXT_CHARACTERS

OUTPUT_COLUMNS = (
    "document_id", "document_title", "text", "category", "source",
    "source_url", "license", "language", "original_metadata",
    "import_status", "review_reason",
)
MISSING = {"", "nan", "none", "null"}


class ImportErrorDetail(ValueError):
    """Raised when the source/configuration cannot safely be imported."""


def _read_records(path: Path, records_key: str | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    suffix = path.suffix.casefold()
    if suffix == ".csv":
        frame = pd.read_csv(path, dtype=object, keep_default_na=False, encoding="utf-8-sig")
        return frame.to_dict(orient="records"), [str(c) for c in frame.columns]
    if suffix == ".parquet":
        try:
            frame = pd.read_parquet(path, engine="pyarrow")
        except ImportError as error:
            raise ImportErrorDetail(
                "Parquet support requires pyarrow. Install it in the project environment with "
                "'.venv/Scripts/python.exe -m pip install pyarrow'."
            ) from error
        except Exception as error:
            raise ImportErrorDetail(f"Could not read Parquet file; it may be invalid or unreadable: {error}") from error
        return frame.to_dict(orient="records"), [str(c) for c in frame.columns]
    if suffix != ".json":
        raise ImportErrorDetail("Supported source formats are CSV, JSON, and Parquet.")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if records_key:
        for part in records_key.split("."):
            if not isinstance(payload, dict) or part not in payload:
                raise ImportErrorDetail(f"Configured JSON records_key was not found: {records_key}")
            payload = payload[part]
    if isinstance(payload, dict):
        if not all(isinstance(value, (dict, list, str, int, float, bool, type(None))) for value in payload.values()):
            raise ImportErrorDetail("JSON object has unsupported nested structure.")
        records = [payload]
    elif isinstance(payload, list) and all(isinstance(row, dict) for row in payload):
        records = payload
    else:
        raise ImportErrorDetail("JSON must be an object, an array of objects, or an object selected by records_key.")
    columns = sorted({str(key) for row in records for key in row})
    return records, columns


def inspect_source(path: str | Path, records_key: str | None = None) -> dict[str, Any]:
    """Report schema and bounded metadata without exposing document text."""
    source = Path(path)
    records, columns = _read_records(source, records_key)
    frame = pd.DataFrame.from_records(records, columns=columns)
    text_columns = [
        column for column in columns
        if any(token in str(column).casefold() for token in ("text", "content", "body"))
    ]
    label_columns = [column for column in columns if any(token in str(column).casefold() for token in ("label", "category", "class"))]
    type_columns = [column for column in columns if "type" in str(column).casefold()]

    def distinct_values(fields: list[str]) -> dict[str, list[str]]:
        values: dict[str, list[str]] = {}
        for field in fields:
            found = frame[field].dropna().astype(str).str.strip()
            found = found[found.ne("")].drop_duplicates().head(20)
            values[field] = [value[:100] for value in found.tolist()]
        return values

    lengths: dict[str, list[int | None]] = {}
    for field in text_columns:
        lengths[field] = [None if pd.isna(value) else len(str(value)) for value in frame[field].head(5)]
    return {
        "file": source.name,
        "format": source.suffix.lstrip(".").casefold(),
        "record_count": len(frame),
        "columns": columns,
        "data_types": {str(column): str(dtype) for column, dtype in frame.dtypes.items()},
        "missing_values": {str(column): int(frame[column].isna().sum() + frame[column].astype(str).str.strip().eq("").sum()) for column in columns},
        "sample_text_lengths": lengths,
        "metadata_fields": [column for column in columns if column not in text_columns],
        "source_labels": distinct_values(label_columns),
        "document_types": distinct_values(type_columns),
    }


def _value(row: dict[str, Any], config: dict[str, Any], target: str) -> str:
    source_column = config.get("column_map", {}).get(target)
    if source_column is None:
        return ""
    value = row.get(source_column, "")
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    result = str(value).strip()
    return "" if result.casefold() in MISSING else result


def _norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _source_details(register_path: Path, source_id: str) -> dict[str, str]:
    frame = pd.read_csv(register_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    required = {"source_id", "source_name", "source_url", "license", "review_status"}
    if not required.issubset(frame.columns):
        raise ImportErrorDetail("Source register is missing required columns: " + ", ".join(sorted(required - set(frame.columns))))
    matches = frame[frame["source_id"].str.strip() == source_id]
    if len(matches) != 1:
        raise ImportErrorDetail("source_id must match exactly one source_register.csv row.")
    details = matches.iloc[0].to_dict()
    if details["review_status"].strip().casefold() != "approved":
        raise ImportErrorDetail("Source rights are not approved in source_register.csv; import was not written.")
    if not all(details[field].strip() for field in ("source_name", "source_url", "license")):
        raise ImportErrorDetail("Approved source register entry must include source name, URL, and license.")
    return {str(k): str(v).strip() for k, v in details.items()}


def import_source(
    input_path: str | Path,
    config_path: str | Path,
    source_register_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
) -> dict[str, Any]:
    """Normalize source records, preserving metadata and flagging review rows.

    Existing output/report files are never overwritten. Unmapped, ambiguous,
    incomplete, short, and duplicate records are retained in staging with an
    explicit status; only mapped, complete unique rows count as imported.
    """
    source_path, cfg_path = Path(input_path), Path(config_path)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
    source_id = str(cfg.get("source_id", "")).strip()
    if not source_id:
        raise ImportErrorDetail("Configuration must specify source_id.")
    source = _source_details(Path(source_register_path), source_id)
    records, columns = _read_records(source_path, cfg.get("records_key"))
    if not records:
        raise ImportErrorDetail("Source dataset is empty; no staging files were written.")
    out_path, rpt_path = Path(output_path), Path(report_path)
    if out_path.exists() or rpt_path.exists():
        raise ImportErrorDetail("Refusing to overwrite an existing output or report.")
    category_map = cfg.get("category_map", {})
    column_map = cfg.get("column_map", {})
    if not isinstance(column_map, dict):
        raise ImportErrorDetail("column_map must be a JSON object of LexiClass fields to source fields.")
    missing_required_mappings = [
        target for target in ("document_id", "document_title", "text")
        if not str(column_map.get(target, "")).strip()
    ]
    if missing_required_mappings:
        raise ImportErrorDetail("Missing required source-field mapping(s): " + ", ".join(missing_required_mappings))
    if not str(column_map.get("language", "")).strip() and not str(cfg.get("default_language", "")).strip():
        raise ImportErrorDetail("Map a language field or provide a verified default_language.")
    if not isinstance(category_map, dict) or any(value not in LEGAL_CATEGORIES for value in category_map.values()):
        raise ImportErrorDetail("category_map values must be one of the five approved category names.")
    basis = str(cfg.get("mapping_basis", "")).strip()
    if category_map and len(basis) < 20:
        raise ImportErrorDetail("A category mapping requires a documented, human-validated mapping_basis (at least 20 characters).")
    mapping_column = column_map.get("category")
    if category_map and not mapping_column:
        raise ImportErrorDetail("A category mapping requires an explicit source category column in column_map.")
    configured_columns = [str(value) for value in column_map.values() if value]
    missing_columns = sorted(set(configured_columns) - set(columns))
    if missing_columns:
        raise ImportErrorDetail("Configured source column(s) not found: " + ", ".join(missing_columns))

    rows: list[dict[str, str]] = []
    duplicate_count = invalid_count = review_count = success_count = 0
    distribution = {category: 0 for category in LEGAL_CATEGORIES}
    id_counts = Counter(_value(row, cfg, "document_id").casefold() for row in records)
    text_counts = Counter(_norm_text(_value(row, cfg, "text")).casefold() for row in records)
    id_counts.pop("", None)
    text_counts.pop("", None)
    for original in records:
        metadata = json.dumps(original, ensure_ascii=False, sort_keys=True, default=str)
        doc_id = _value(original, cfg, "document_id")
        title = _value(original, cfg, "document_title")
        text = _value(original, cfg, "text")
        category_source = _value(original, cfg, "category")
        category = category_map.get(category_source, "REVIEW_REQUIRED") if category_source else "REVIEW_REQUIRED"
        direct_url = _value(original, cfg, "source_url")
        language = _value(original, cfg, "language") or str(cfg.get("default_language", "")).strip()
        normalized = _norm_text(text)
        reasons: list[str] = []
        if not doc_id: reasons.append("missing document_id")
        if not title: reasons.append("missing document_title")
        if not text: reasons.append("missing text")
        if len(normalized) < MIN_DOCUMENT_TEXT_CHARACTERS: reasons.append("text is empty or shorter than 100 characters")
        if not language: reasons.append("missing language")
        if not category_source or category == "REVIEW_REQUIRED": reasons.append("category needs manual review; source label was not mapped")
        duplicate = bool((doc_id and id_counts[doc_id.casefold()] > 1) or (normalized and text_counts[normalized.casefold()] > 1))
        if duplicate:
            duplicate_count += 1
            reasons.append("duplicate document ID or normalized text")
        required_missing = not all((doc_id, title, text, language))
        is_invalid = required_missing or len(normalized) < MIN_DOCUMENT_TEXT_CHARACTERS
        if is_invalid:
            invalid_count += 1
        if duplicate or is_invalid or category == "REVIEW_REQUIRED":
            review_count += 1
            status = "REVIEW_REQUIRED" if category == "REVIEW_REQUIRED" or duplicate else "INVALID"
        else:
            status = "IMPORTED"
            success_count += 1
            distribution[category] += 1
        rows.append({
            "document_id": doc_id, "document_title": title, "text": normalized,
            "category": category, "source": source_id, "source_url": direct_url,
            "license": source["license"], "language": language,
            "original_metadata": metadata, "import_status": status,
            "review_reason": "; ".join(reasons),
        })
    output = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rpt_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(out_path, index=False, encoding="utf-8-sig")
    report = {
        "source_name": source["source_name"], "source_id": source_id,
        "source_format": source_path.suffix.lstrip(".").casefold(),
        "original_source_columns": columns, "original_records": len(records),
        "successfully_imported_records": success_count,
        "duplicate_records": duplicate_count, "invalid_records": invalid_count,
        "records_requiring_manual_review": review_count,
        "category_distribution": distribution,
        "note": "Only unique, complete rows with explicitly mapped categories count as imported. No ML training was performed.",
    }
    rpt_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or import a licensed source dataset.")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Inspect source file fields and record count.")
    inspect.add_argument("input")
    inspect.add_argument("--records-key")
    run = sub.add_parser("import", help="Import into a non-overwriting staging CSV and JSON report.")
    for name in ("input", "config", "source-register", "output", "report"):
        run.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            result = inspect_source(args.input, args.records_key)
        else:
            result = import_source(args.input, args.config, args.source_register, args.output, args.report)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, json.JSONDecodeError, pd.errors.ParserError, ImportErrorDetail) as error:
        print(f"Import stopped: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
