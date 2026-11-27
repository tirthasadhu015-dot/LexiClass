"""Tests for training preconditions that do not create synthetic legal data."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.model_training import DatasetTrainingError, train_and_evaluate
from src.dataset_validation import REQUIRED_COLUMNS


class ModelTrainingPreconditionTests(unittest.TestCase):
    def test_empty_dataset_is_rejected_without_creating_model_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset_path = Path(temporary_directory) / "legal_documents.csv"
            pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(dataset_path, index=False)
            model_directory = Path(temporary_directory) / "models"
            with self.assertRaisesRegex(DatasetTrainingError, "0 labeled records"):
                train_and_evaluate(dataset_path, model_directory)
            self.assertFalse(model_directory.exists())


if __name__ == "__main__":
    unittest.main()
