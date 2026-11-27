"""Validation and reporting for the LexiClass AI CSV dataset."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


LEGAL_CATEGORIES = (
    "Criminal Law",
    "Civil Law",
    "Constitutional Law",
    "Property Law",
    "Other Legal Domains",
)

REQUIRED_COLUMNS = (
    "document_id",
    "document_title",
    "text",
    "category",
    "source",
    "source_url",
    "license",
    "language",
)
REQUIRED_VALUE_COLUMNS = (
    "document_id",
    "document_title",
    "text",
    "category",
    "source",
    "license",
    "language",
)
MIN_DOCUMENT_TEXT_CHARACTERS = 100


@dataclass(frozen=True)
class DatasetValidationReport:
    """Summary of dataset validation findings and category counts."""

    row_count: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    class_distribution: dict[str, int]

    @property
    def is_valid(self) -> bool:
        """Whether all present records satisfy the dataset rules."""

        return not self.errors

    @property
    def is_ready_for_training(self) -> bool:
        """Whether the dataset is valid and contains at least one record."""

        return self.is_valid and self.row_count > 0


def _clean_column(values: pd.Series) -> pd.Series:
    """Convert values to trimmed strings while treating nulls as empty."""

    return values.fillna("").astype(str).str.strip()


def validate_dataset(dataframe: pd.DataFrame) -> DatasetValidationReport:
    """Validate dataset columns, required values, categories, and duplicates.

    ``source_url`` is part of the schema but may be blank when a document has
    no direct URL, provided the source is traceable through ``source`` and the
    source register. License information is required for each record.
    """

    errors: list[str] = []
    warnings: list[str] = []
    distribution = {category: 0 for category in LEGAL_CATEGORIES}
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]

    if missing_columns:
        errors.append("Missing required columns: " + ", ".join(missing_columns))
        return DatasetValidationReport(
            row_count=len(dataframe),
            errors=tuple(errors),
            warnings=tuple(warnings),
            class_distribution=distribution,
        )

    if dataframe.empty:
        warnings.append("The CSV has no records; it is a template and is not ready for training.")
        return DatasetValidationReport(
            row_count=0,
            errors=(),
            warnings=tuple(warnings),
            class_distribution=distribution,
        )

    cleaned = {column: _clean_column(dataframe[column]) for column in REQUIRED_COLUMNS}

    for column in REQUIRED_VALUE_COLUMNS:
        missing_count = int(cleaned[column].eq("").sum())
        if missing_count:
            errors.append(f"Missing {column} values: {missing_count} row(s).")

    missing_source_urls = int(cleaned["source_url"].eq("").sum())
    if missing_source_urls:
        warnings.append(
            f"Missing source_url values: {missing_source_urls} row(s); verify that source attribution is traceable in source_register.csv."
        )

    short_text_count = int(
        cleaned["text"].map(lambda value: 0 < len(re.sub(r"\s+", " ", value)) < MIN_DOCUMENT_TEXT_CHARACTERS).sum()
    )
    if short_text_count:
        errors.append(
            f"Unusually short document text (<{MIN_DOCUMENT_TEXT_CHARACTERS} characters): "
            f"{short_text_count} row(s); manually review or exclude before training."
        )

    labels = cleaned["category"]
    invalid_labels = sorted(set(labels[labels.ne("")]) - set(LEGAL_CATEGORIES))
    if invalid_labels:
        errors.append("Invalid category label(s): " + ", ".join(invalid_labels))

    valid_labels = labels[labels.isin(LEGAL_CATEGORIES)]
    counted = valid_labels.value_counts()
    for category in LEGAL_CATEGORIES:
        distribution[category] = int(counted.get(category, 0))

    normalized_ids = cleaned["document_id"].str.casefold()
    nonempty_ids = normalized_ids.ne("")
    duplicate_id_rows = int(normalized_ids[nonempty_ids].duplicated(keep=False).sum())
    if duplicate_id_rows:
        errors.append(f"Duplicate document_id values: {duplicate_id_rows} row(s) are part of a duplicate group.")

    normalized_text = cleaned["text"].str.casefold().map(lambda value: re.sub(r"\s+", " ", value))
    nonempty_text = normalized_text.ne("")
    duplicate_text_rows = int(normalized_text[nonempty_text].duplicated(keep=False).sum())
    if duplicate_text_rows:
        errors.append(f"Duplicate normalized document text: {duplicate_text_rows} row(s) are part of a duplicate group.")

    return DatasetValidationReport(
        row_count=len(dataframe),
        errors=tuple(errors),
        warnings=tuple(warnings),
        class_distribution=distribution,
    )


def load_and_validate_dataset(csv_path: str | Path) -> tuple[pd.DataFrame, DatasetValidationReport]:
    """Load a CSV as strings and return its validation report."""

    path = Path(csv_path)
    try:
        dataframe = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except (OSError, pd.errors.ParserError, UnicodeError) as error:
        report = DatasetValidationReport(
            row_count=0,
            errors=(f"Could not read dataset CSV: {error}",),
            warnings=(),
            class_distribution={category: 0 for category in LEGAL_CATEGORIES},
        )
        return pd.DataFrame(columns=REQUIRED_COLUMNS), report

    return dataframe, validate_dataset(dataframe)


def main() -> int:
    """Print validation results and category distribution for a CSV file."""

    parser = argparse.ArgumentParser(description="Validate the LexiClass AI dataset CSV.")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="dataset/legal_documents.csv",
        help="Path to the dataset CSV (default: dataset/legal_documents.csv)",
    )
    args = parser.parse_args()
    _, report = load_and_validate_dataset(args.csv_path)

    print(f"Rows: {report.row_count}")
    print("Class distribution:")
    for category, count in report.class_distribution.items():
        print(f"  {category}: {count}")
    for warning in report.warnings:
        print(f"Warning: {warning}")
    for error in report.errors:
        print(f"Error: {error}")

    if report.is_ready_for_training:
        print("Dataset validation passed; training readiness still depends on dataset sufficiency and quality.")
        return 0
    if report.is_valid:
        print("Dataset structure is valid, but there are no records to train on.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())



