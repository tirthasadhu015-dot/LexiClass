"""Tests for training preconditions that do not create synthetic legal data."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.model_training import DatasetTrainingError, train_and_evaluate


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ModelTrainingPreconditionTests(unittest.TestCase):
    def test_empty_dataset_is_rejected_without_creating_model_artifacts(self) -> None:
        dataset_path = PROJECT_ROOT / "dataset" / "legal_documents.csv"
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(DatasetTrainingError, "0 labeled records"):
                train_and_evaluate(dataset_path, temporary_directory)
            self.assertEqual(list(Path(temporary_directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
