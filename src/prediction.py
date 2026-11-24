"""Load trained artifacts and classify preprocessed document text."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from src.data_preprocessing import preprocess_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models"
CLASSIFIER_FILENAME = "classifier.joblib"
VECTORIZER_FILENAME = "tfidf_vectorizer.joblib"


class ModelArtifactError(RuntimeError):
    """Raised when trained classifier/vectorizer artifacts are unavailable."""


def load_model_artifacts(model_dir: str | Path = DEFAULT_MODEL_DIR) -> tuple[Any, Any]:
    """Load the classifier and its paired fitted TF-IDF vectorizer."""

    directory = Path(model_dir)
    classifier_path = directory / CLASSIFIER_FILENAME
    vectorizer_path = directory / VECTORIZER_FILENAME
    missing = [path.name for path in (classifier_path, vectorizer_path) if not path.is_file()]
    if missing:
        raise ModelArtifactError(
            "Trained model artifacts are missing: " + ", ".join(missing) + ". Run train_model.py after preparing the dataset."
        )
    try:
        return joblib.load(classifier_path), joblib.load(vectorizer_path)
    except Exception as error:
        raise ModelArtifactError("The saved model artifacts could not be loaded.") from error


def predict_category(
    text: str,
    *,
    classifier: Any | None = None,
    vectorizer: Any | None = None,
    model_dir: str | Path = DEFAULT_MODEL_DIR,
) -> str:
    """Predict a category using the same fitted vectorizer used in training."""

    if not isinstance(text, str) or not preprocess_text(text):
        raise ValueError("Document text must be a non-empty string.")
    if (classifier is None) != (vectorizer is None):
        raise ValueError("Provide both classifier and vectorizer, or neither.")
    if classifier is None:
        classifier, vectorizer = load_model_artifacts(model_dir)

    try:
        features = vectorizer.transform([text])
        prediction = classifier.predict(features)[0]
    except Exception as error:
        raise ModelArtifactError("The document could not be transformed or classified.") from error
    return str(prediction)
