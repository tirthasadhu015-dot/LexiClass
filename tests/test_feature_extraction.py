"""Tests for TF-IDF fitting and inference-time transformation."""

from __future__ import annotations

import unittest

from src.feature_extraction import (
    FeatureExtractionError,
    fit_tfidf_vectorizer,
    transform_texts,
)


class TfidfFeatureExtractionTests(unittest.TestCase):
    def test_fitted_vectorizer_transforms_new_text_without_refitting(self) -> None:
        vectorizer, training_features = fit_tfidf_vectorizer(
            ["alpha beta not gamma", "beta delta without epsilon"]
        )
        vocabulary_before = dict(vectorizer.vocabulary_)

        inference_features = transform_texts(vectorizer, ["alpha not epsilon"])

        self.assertEqual(training_features.shape[1], inference_features.shape[1])
        self.assertEqual(vectorizer.vocabulary_, vocabulary_before)
        self.assertIn("not", vectorizer.vocabulary_)

    def test_rejects_empty_or_blank_training_text(self) -> None:
        with self.assertRaises(FeatureExtractionError):
            fit_tfidf_vectorizer([])
        with self.assertRaises(FeatureExtractionError):
            fit_tfidf_vectorizer(["   "])


if __name__ == "__main__":
    unittest.main()
