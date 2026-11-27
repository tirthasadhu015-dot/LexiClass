"""Evaluation precondition tests using the actual empty project dataset."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.evaluation import EvaluationUnavailableError, evaluate_models
from src.dataset_validation import REQUIRED_COLUMNS


class EvaluationPreconditionTests(unittest.TestCase):
    def test_empty_dataset_does_not_create_reports_or_figures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset_path = Path(temporary_directory) / "legal_documents.csv"
            pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(dataset_path, index=False)
            report_directory = Path(temporary_directory) / "evaluation"
            with self.assertRaisesRegex(EvaluationUnavailableError, "0 labeled records"):
                evaluate_models(dataset_path, report_dir=report_directory)
            self.assertFalse(report_directory.exists())


if __name__ == "__main__":
    unittest.main()
