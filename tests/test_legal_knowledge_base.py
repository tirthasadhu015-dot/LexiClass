"""Tests for isolated legal-reference processing and search helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.legal_knowledge_base import (
    LegalKnowledgeBaseError,
    load_reference_csv,
    load_reference_json,
    prepare_reference_records,
    process_reference_json,
    search_legal_references,
)


def sample_record(**updates: str) -> dict[str, str]:
    record = {
        "code": "IPC",
        "section": "Section 1",
        "title": "Test legal title",
        "description": "A sample statutory description.",
        "purpose": "Sample purpose.",
        "context": "Sample context.",
        "penalty": "Refer to source.",
        "keywords": "sample keyword alpha",
        "source_url": "https://www.indiacode.nic.in/example?section=1&view=full",
        "source_name": "India Code",
    }
    record.update(updates)
    return record


class LegalKnowledgeBaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_loads_utf8_json_list(self) -> None:
        path = self.root / "references.json"
        path.write_text(json.dumps([sample_record(title="संविधान test")], ensure_ascii=False), encoding="utf-8")
        records = load_reference_json(path)
        self.assertEqual(records[0]["title"], "संविधान test")

    def test_invalid_json_is_reported(self) -> None:
        path = self.root / "invalid.json"
        path.write_text("{ broken", encoding="utf-8")
        with self.assertRaisesRegex(LegalKnowledgeBaseError, "Could not read"):
            load_reference_json(path)

    def test_non_list_json_root_is_rejected(self) -> None:
        path = self.root / "object.json"
        path.write_text(json.dumps({"record": sample_record()}), encoding="utf-8")
        with self.assertRaisesRegex(LegalKnowledgeBaseError, "root must be a list"):
            load_reference_json(path)

    def test_missing_values_are_counted_and_incomplete_row_is_retained(self) -> None:
        record = sample_record(source_url="", source_name="")
        frame, report = prepare_reference_records([record])
        self.assertEqual(len(frame), 1)
        self.assertEqual(report["incomplete_records"], 1)
        self.assertEqual(report["missing_values_by_field"]["source_url"], 1)
        self.assertEqual(frame.loc[0, "source_url"], "")

    def test_non_dictionary_record_is_counted_as_invalid(self) -> None:
        frame, report = prepare_reference_records([sample_record(), "malformed record"])
        self.assertEqual(len(frame), 1)
        self.assertEqual(report["invalid_records"], 1)

    def test_duplicate_records_are_counted_and_not_exported_twice(self) -> None:
        record = sample_record()
        frame, report = prepare_reference_records([record, dict(record)])
        self.assertEqual(len(frame), 1)
        self.assertEqual(report["duplicate_records"], 1)
        self.assertEqual(report["duplicate_record_indices_zero_based"], [1])

    def test_csv_export_report_and_source_url_are_preserved(self) -> None:
        source = self.root / "source.json"
        output = self.root / "processed" / "legal_reference.csv"
        report_path = self.root / "processed" / "inspection_report.json"
        record = sample_record()
        source.write_text(json.dumps([record], ensure_ascii=False), encoding="utf-8")
        report = process_reference_json(source, output, report_path)
        exported = load_reference_csv(output)
        self.assertEqual(report["successfully_processed_records"], 1)
        self.assertEqual(report["skipped_records"], 0)
        self.assertEqual(exported[0]["source_url"], record["source_url"])
        self.assertEqual(exported[0]["source_name"], record["source_name"])
        saved_report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertIn("processing_timestamp_utc", saved_report)
        self.assertEqual(saved_report["records_grouped_by_code"], {"IPC": 1})

    def test_search_by_code_is_case_insensitive_exact(self) -> None:
        records = [sample_record(), sample_record(code="BNS", section="Section 2")]
        matches = search_legal_references(records, code="ipc")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["code"], "IPC")

    def test_search_by_section_accepts_number_or_label(self) -> None:
        records = [sample_record(), sample_record(section="Section 2")]
        matches = search_legal_references(records, section="1")
        self.assertEqual([row["section"] for row in matches], ["Section 1"])

    def test_search_by_title(self) -> None:
        matches = search_legal_references([sample_record()], query="legal title")
        self.assertEqual(len(matches), 1)

    def test_search_by_keywords(self) -> None:
        matches = search_legal_references([sample_record()], query="alpha")
        self.assertEqual(len(matches), 1)

    def test_combined_search_and_empty_search_results(self) -> None:
        records = [sample_record(), sample_record(code="BNS", section="Section 2")]
        self.assertEqual(len(search_legal_references(records, code="IPC", query="alpha")), 1)
        self.assertEqual(search_legal_references(records, query="does-not-exist"), [])
        self.assertEqual(search_legal_references(records), [])


if __name__ == "__main__":
    unittest.main()
