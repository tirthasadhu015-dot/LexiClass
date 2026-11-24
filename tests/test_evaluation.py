"""Evaluation precondition tests using the actual empty project dataset."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.evaluation import EvaluationUnavailableError, evaluate_models


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class EvaluationPreconditionTests(unittest.TestCase):
    def test_empty_dataset_does_not_create_reports_or_figures(self) -> None:
        dataset_path = PROJECT_ROOT / "dataset" / "legal_documents.csv"
        with tempfile.TemporaryDirectory() as temporary_directory:
            report_directory = Path(temporary_directory) / "evaluation"
            with self.assertRaisesRegex(EvaluationUnavailableError, "0 labeled records"):
                evaluate_models(dataset_path, report_dir=report_directory)
            self.assertFalse(report_directory.exists())


if __name__ == "__main__":
    unittest.main()
