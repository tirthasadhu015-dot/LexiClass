"""Tests use isolated temporary technical fixtures, never dataset/ training data."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.dataset_import import ImportErrorDetail, import_source, inspect_source


class DatasetImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source_register = self.root / "source_register.csv"
        pd.DataFrame([{
            "source_id": "fixture-source", "source_name": "Temporary test fixture",
            "source_url": "https://example.invalid/fixture", "dataset_version": "test-only",
            "format": "Parquet", "license": "TEST ONLY", "license_url": "",
            "terms_url": "", "accessed_on": "", "attribution": "",
            "usage_notes": "Temporary automated test fixture; not legal corpus data.",
            "review_status": "approved",
        }]).to_csv(self.source_register, index=False)
        self.text = "Temporary test fixture text. " + ("Reserved technical test content. " * 5)
        self.config = {
            "source_id": "fixture-source",
            "column_map": {
                "document_id": "source_id", "document_title": "title",
                "text": "body", "category": "source_label",
                "source_url": "url", "language": "lang",
            },
            "default_language": "en",
            "records_key": None,
            "category_map": {"fixture-label": "Civil Law"},
            "mapping_basis": "Mapping exists only to test explicit config behavior.",
        }
        self.config_path = self.root / "config.json"
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _row(self, **overrides: str) -> dict[str, str]:
        row = {
            "source_id": "fixture-001", "title": "Temporary fixture title",
            "body": self.text, "source_label": "fixture-label",
            "url": "https://example.invalid/document", "lang": "en",
        }
        row.update(overrides)
        return row

    def _import(self, source_path: Path, config: dict | None = None) -> tuple[dict, pd.DataFrame]:
        if config is not None:
            self.config_path.write_text(json.dumps(config), encoding="utf-8")
        output, report = self.root / "stage.csv", self.root / "report.json"
        summary = import_source(source_path, self.config_path, self.source_register, output, report)
        return summary, pd.read_csv(output, keep_default_na=False)

    def test_parquet_inspection_reports_schema_counts_and_text_lengths_without_text(self) -> None:
        path = self.root / "source.parquet"
        pd.DataFrame([self._row(), self._row(source_id="fixture-002")]).to_parquet(path, index=False)
        details = inspect_source(path)
        self.assertEqual(details["record_count"], 2)
        self.assertIn("body", details["columns"])
        self.assertIn("body", details["sample_text_lengths"])
        self.assertEqual(len(details["sample_text_lengths"]["body"]), 2)
        self.assertEqual(details["source_labels"]["source_label"], ["fixture-label"])
        self.assertNotIn(self.text, json.dumps(details))

    def test_explicit_field_mapping_imports_and_preserves_original_metadata(self) -> None:
        path = self.root / "source.parquet"
        pd.DataFrame([self._row()]).to_parquet(path, index=False)
        report, imported = self._import(path)
        self.assertEqual(report["successfully_imported_records"], 1)
        self.assertEqual(imported.loc[0, "category"], "Civil Law")
        self.assertEqual(json.loads(imported.loc[0, "original_metadata"])["source_label"], "fixture-label")

    def test_unmapped_category_stays_review_required(self) -> None:
        path = self.root / "source.csv"
        pd.DataFrame([self._row(source_label="unmapped")]).to_csv(path, index=False)
        report, imported = self._import(path)
        self.assertEqual(report["successfully_imported_records"], 0)
        self.assertEqual(imported.loc[0, "category"], "REVIEW_REQUIRED")

    def test_configured_missing_field_is_rejected(self) -> None:
        path = self.root / "source.csv"
        pd.DataFrame([self._row()]).to_csv(path, index=False)
        config = dict(self.config)
        config["column_map"] = dict(self.config["column_map"], text="missing_text_field")
        with self.assertRaisesRegex(ImportErrorDetail, "Configured source column"):
            self._import(path, config)

    def test_required_mapping_must_be_supplied(self) -> None:
        path = self.root / "source.csv"
        pd.DataFrame([self._row()]).to_csv(path, index=False)
        config = dict(self.config)
        config["column_map"] = dict(self.config["column_map"], text="")
        with self.assertRaisesRegex(ImportErrorDetail, "Missing required source-field mapping"):
            self._import(path, config)

    def test_invalid_category_mapping_is_rejected(self) -> None:
        path = self.root / "source.csv"
        pd.DataFrame([self._row()]).to_csv(path, index=False)
        config = dict(self.config)
        config["category_map"] = {"fixture-label": "Not a category"}
        with self.assertRaisesRegex(ImportErrorDetail, "five approved"):
            self._import(path, config)

    def test_duplicate_records_are_all_flagged(self) -> None:
        path = self.root / "source.parquet"
        pd.DataFrame([self._row(), self._row()]).to_parquet(path, index=False)
        report, imported = self._import(path)
        self.assertEqual(report["duplicate_records"], 2)
        self.assertEqual(report["successfully_imported_records"], 0)
        self.assertTrue((imported["import_status"] == "REVIEW_REQUIRED").all())

    def test_empty_parquet_inspects_zero_and_import_refuses_it(self) -> None:
        path = self.root / "empty.parquet"
        pd.DataFrame(columns=["source_id", "body"]).to_parquet(path, index=False)
        self.assertEqual(inspect_source(path)["record_count"], 0)
        with self.assertRaisesRegex(ImportErrorDetail, "empty"):
            self._import(path)

    def test_missing_parquet_engine_has_actionable_error(self) -> None:
        path = self.root / "source.parquet"
        path.write_bytes(b"not read because engine is mocked")
        with patch("src.dataset_import.pd.read_parquet", side_effect=ImportError("no engine")):
            with self.assertRaisesRegex(ImportErrorDetail, "requires pyarrow"):
                inspect_source(path)

    def test_invalid_parquet_has_clear_error(self) -> None:
        path = self.root / "invalid.parquet"
        path.write_bytes(b"not a parquet file")
        with self.assertRaisesRegex(ImportErrorDetail, "may be invalid or unreadable"):
            inspect_source(path)

    def test_unsupported_format_is_rejected(self) -> None:
        path = self.root / "source.xlsx"
        path.write_bytes(b"fixture")
        with self.assertRaisesRegex(ImportErrorDetail, "CSV, JSON, and Parquet"):
            inspect_source(path)


if __name__ == "__main__":
    unittest.main()
