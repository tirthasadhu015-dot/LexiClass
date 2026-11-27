"""Temporary-file tests for the manual annotation review workflow."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.annotation_review import (
    ANNOTATION_COLUMNS,
    AnnotationReviewError,
    TARGET_CATEGORIES,
    atomic_save_annotations,
    next_pending_index,
    read_annotations,
    run_review,
    validate_annotation_values,
)


class AnnotationReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.csv_path = self.root / "annotations.csv"
        self.parquet_path = self.root / "documents.parquet"
        pd.DataFrame([
            {"document_id": "fixture-1", "document_title": "Fixture one", "category": "", "annotation_notes": "", "reviewer_status": "PENDING"},
            {"document_id": "fixture-2", "document_title": "Fixture two", "category": "", "annotation_notes": "", "reviewer_status": "PENDING"},
        ], columns=ANNOTATION_COLUMNS).to_csv(self.csv_path, index=False)
        pd.DataFrame([
            {"doc_id": "fixture-1", "document_title": "Fixture one", "document_type": "test", "document_jurisdiction": "test", "issuing_authority": "test", "text": "Temporary test text for annotation review."},
            {"doc_id": "fixture-2", "document_title": "Fixture two", "document_type": "test", "document_jurisdiction": "test", "issuing_authority": "test", "text": "Second temporary test text for annotation review."},
        ]).to_parquet(self.parquet_path, index=False)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_category_validation_accepts_only_approved_labels_and_states(self) -> None:
        for category in TARGET_CATEGORIES:
            validate_annotation_values(category, "ADJUDICATED")
        validate_annotation_values("REVIEW_REQUIRED", "REVIEW_REQUIRED")
        validate_annotation_values("", "PENDING")
        with self.assertRaises(AnnotationReviewError):
            validate_annotation_values("Unknown Law", "ADJUDICATED")
        with self.assertRaises(AnnotationReviewError):
            validate_annotation_values("Civil Law", "PENDING")
        with self.assertRaises(AnnotationReviewError):
            validate_annotation_values("Other Legal Domains", "DONE")

    def test_save_writes_csv_atomically_and_preserves_rows(self) -> None:
        frame, original_hash = read_annotations(self.csv_path)
        frame.at[0, "category"] = "Civil Law"
        frame.at[0, "annotation_notes"] = "Reviewer rationale recorded manually."
        frame.at[0, "reviewer_status"] = "ADJUDICATED"
        new_hash = atomic_save_annotations(frame, self.csv_path, expected_hash=original_hash)
        self.assertNotEqual(new_hash, original_hash)
        saved, saved_hash = read_annotations(self.csv_path)
        self.assertEqual(saved_hash, new_hash)
        self.assertEqual(saved.at[0, "category"], "Civil Law")
        self.assertEqual(saved.at[1, "reviewer_status"], "PENDING")

    def test_resume_selects_next_pending_document_after_first_is_saved(self) -> None:
        responses = iter(["2", "Manual test rationale", "q"])
        messages: list[str] = []
        result = run_review(
            self.parquet_path,
            self.csv_path,
            input_fn=lambda _prompt: next(responses),
            output_fn=messages.append,
        )
        self.assertEqual(result, 0)
        saved, _ = read_annotations(self.csv_path)
        self.assertEqual(saved.at[0, "category"], "Civil Law")
        self.assertEqual(saved.at[0, "reviewer_status"], "ADJUDICATED")
        self.assertEqual(saved.at[1, "reviewer_status"], "PENDING")
        self.assertEqual(next_pending_index(saved), 1)
        self.assertTrue(any("Next PENDING document: fixture-2" in message for message in messages))

    def test_source_parquet_is_unchanged_by_review(self) -> None:
        before = self.parquet_path.read_bytes()
        responses = iter(["q"])
        run_review(
            self.parquet_path,
            self.csv_path,
            input_fn=lambda _prompt: next(responses),
            output_fn=lambda _message: None,
        )
        self.assertEqual(self.parquet_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
