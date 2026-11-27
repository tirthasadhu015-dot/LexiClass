"""Tests for the labeled legal-document dataset schema and quality checks."""

from __future__ import annotations

import unittest

import pandas as pd

from src.dataset_validation import (
    LEGAL_CATEGORIES,
    REQUIRED_COLUMNS,
    validate_dataset,
)


def valid_record(**overrides: str) -> dict[str, str]:
    row = {
        "document_id": "case-001",
        "document_title": "Reviewed civil judgment",
        "text": (
            "This reviewed legal judgment concerns a civil dispute between the parties. "
            "The court considered the applicable statutory provisions and the evidence. "
            "The parties submitted arguments and the decision records the relevant findings."
        ),
        "category": "Civil Law",
        "source": "SRC-001",
        "source_url": "https://example.org/legal-document",
        "license": "CC BY 4.0",
        "language": "en",
    }
    row.update(overrides)
    return row


class DatasetValidationTests(unittest.TestCase):
    def test_empty_template_schema_is_valid_but_not_training_ready(self) -> None:
        report = validate_dataset(pd.DataFrame(columns=REQUIRED_COLUMNS))

        self.assertEqual(report.row_count, 0)
        self.assertFalse(report.is_ready_for_training)
        self.assertEqual(report.class_distribution, {category: 0 for category in LEGAL_CATEGORIES})

    def test_valid_record_has_expected_category_count(self) -> None:
        report = validate_dataset(pd.DataFrame([valid_record()]))

        self.assertTrue(report.is_valid, report.errors)
        self.assertEqual(report.class_distribution["Civil Law"], 1)

    def test_missing_text_category_source_and_license_are_reported(self) -> None:
        report = validate_dataset(
            pd.DataFrame(
                [
                    valid_record(text="", category="", source="", license=""),
                ]
            )
        )

        joined_errors = " ".join(report.errors)
        for field in ("text", "category", "source", "license"):
            self.assertIn(f"Missing {field}", joined_errors)

    def test_invalid_category_is_rejected(self) -> None:
        report = validate_dataset(pd.DataFrame([valid_record(category="Civil/Property")]))

        self.assertTrue(any("Invalid category" in error for error in report.errors))

    def test_duplicate_ids_and_normalized_text_are_rejected(self) -> None:
        first = valid_record()
        second = valid_record(
            document_id="CASE-001",
            document_title="Reformatted duplicate",
            text=first["text"].upper().replace("  ", " "),
        )
        report = validate_dataset(pd.DataFrame([first, second]))

        joined_errors = " ".join(report.errors)
        self.assertIn("Duplicate document_id", joined_errors)
        self.assertIn("Duplicate normalized document text", joined_errors)

    def test_short_text_is_flagged_for_manual_review(self) -> None:
        report = validate_dataset(pd.DataFrame([valid_record(text="Section 1 applies.")]))

        self.assertTrue(any("Unusually short" in error for error in report.errors))

    def test_missing_direct_url_is_a_warning_when_source_is_traceable(self) -> None:
        report = validate_dataset(pd.DataFrame([valid_record(source_url="")]))

        self.assertTrue(report.is_valid, report.errors)
        self.assertTrue(any("source_url" in warning for warning in report.warnings))


if __name__ == "__main__":
    unittest.main()
