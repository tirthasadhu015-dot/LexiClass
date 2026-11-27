"""Tests for prediction preconditions and supported categories."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from src.dataset_validation import LEGAL_CATEGORIES
from src.prediction import (
    CLASSIFIER_FILENAME,
    VECTORIZER_FILENAME,
    ModelArtifactError,
    load_model_artifacts,
    model_artifacts_available,
    predict_category,
    predict_category_with_confidence,
)
from src.feature_extraction import fit_tfidf_vectorizer


class PredictionPreconditionTests(unittest.TestCase):
    def test_supported_categories_are_complete_and_ordered(self) -> None:
        self.assertEqual(
            LEGAL_CATEGORIES,
            (
                "Criminal Law",
                "Civil Law",
                "Constitutional Law",
                "Property Law",
                "Other Legal Domains",
            ),
        )

    def test_missing_model_and_vectorizer_are_reported_without_artifact_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            model_dir = Path(temporary_directory)

            self.assertFalse(model_artifacts_available(model_dir))
            with self.assertRaises(ModelArtifactError) as raised:
                load_model_artifacts(model_dir)

            self.assertIn(CLASSIFIER_FILENAME, str(raised.exception))
            self.assertIn(VECTORIZER_FILENAME, str(raised.exception))
            self.assertEqual(list(model_dir.iterdir()), [])

    def test_reports_missing_classifier_independently(self) -> None:
        with patch("src.prediction.Path.is_file") as is_file:
            is_file.side_effect = [False, True]

            with self.assertRaisesRegex(ModelArtifactError, CLASSIFIER_FILENAME):
                load_model_artifacts("unused-model-dir")

    def test_reports_missing_vectorizer_independently(self) -> None:
        with patch("src.prediction.Path.is_file") as is_file:
            is_file.side_effect = [True, False]

            with self.assertRaisesRegex(ModelArtifactError, VECTORIZER_FILENAME):
                load_model_artifacts("unused-model-dir")

    def test_unreadable_artifacts_are_reported_safely(self) -> None:
        with (
            patch("src.prediction.Path.is_file", return_value=True),
            patch("src.prediction.joblib.load", side_effect=ValueError("internal parser detail")),
        ):
            with self.assertRaisesRegex(ModelArtifactError, "could not be loaded") as raised:
                load_model_artifacts("unused-model-dir")

        self.assertNotIn("internal parser detail", str(raised.exception))

    def test_empty_text_is_rejected_before_artifact_loading(self) -> None:
        with patch("src.prediction.load_model_artifacts") as load_artifacts:
            with self.assertRaisesRegex(ValueError, "non-empty"):
                predict_category("  \n\t")

        load_artifacts.assert_not_called()

    def test_classifier_and_vectorizer_must_be_provided_together(self) -> None:
        with self.assertRaisesRegex(ValueError, "both classifier and vectorizer"):
            predict_category("A legal document", classifier=object())

    def test_prediction_contract_accepts_each_supported_category(self) -> None:
        for category in LEGAL_CATEGORIES:
            with self.subTest(category=category):
                vectorizer, _ = fit_tfidf_vectorizer(
                    ["Section 12 applies; the claim shall not be waived."]
                )
                classifier = Mock()
                classifier.predict.return_value = [category]

                prediction, probability = predict_category_with_confidence(
                    "Section 12 applies to this legal document.",
                    classifier=classifier,
                    vectorizer=vectorizer,
                )

                self.assertEqual(prediction, category)
                self.assertIsNone(probability)
                classifier.predict.assert_called_once()

    def test_unsupported_model_output_is_rejected(self) -> None:
        vectorizer, _ = fit_tfidf_vectorizer(["Section 12 legal document claim."])
        classifier = Mock()
        classifier.predict.return_value = ["Unsupported Category"]

        with self.assertRaisesRegex(ModelArtifactError, "unsupported legal category"):
            predict_category_with_confidence(
                "Section 12 applies to this legal document.",
                classifier=classifier,
                vectorizer=vectorizer,
            )


if __name__ == "__main__":
    unittest.main()
