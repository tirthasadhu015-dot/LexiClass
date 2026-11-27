"""Load trained artifacts and classify document text."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from src.data_preprocessing import preprocess_text
from src.dataset_validation import LEGAL_CATEGORIES
from src.feature_extraction import transform_texts


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models"
CLASSIFIER_FILENAME = "classifier.joblib"
VECTORIZER_FILENAME = "tfidf_vectorizer.joblib"


class ModelArtifactError(RuntimeError):
    """Raised when trained classifier/vectorizer artifacts are unavailable."""


def model_artifacts_available(model_dir: str | Path = DEFAULT_MODEL_DIR) -> bool:
    """Return whether both inference artifacts are present."""

    directory = Path(model_dir)
    return all(
        (directory / filename).is_file()
        for filename in (CLASSIFIER_FILENAME, VECTORIZER_FILENAME)
    )


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


def predict_category_with_confidence(
    text: str,
    *,
    classifier: Any | None = None,
    vectorizer: Any | None = None,
    model_dir: str | Path = DEFAULT_MODEL_DIR,
) -> tuple[str, float | None]:
    """Predict a category and return probability only if the model supports it."""

    if not isinstance(text, str):
        raise ValueError("Document text must be a non-empty string.")
    processed_text = preprocess_text(text)
    if not processed_text:
        raise ValueError("Document text must be a non-empty string.")
    if (classifier is None) != (vectorizer is None):
        raise ValueError("Provide both classifier and vectorizer, or neither.")
    if classifier is None:
        classifier, vectorizer = load_model_artifacts(model_dir)

    try:
        features = transform_texts(vectorizer, [processed_text])
        prediction = classifier.predict(features)[0]
    except Exception as error:
        raise ModelArtifactError("The document could not be transformed or classified.") from error
    if prediction not in LEGAL_CATEGORIES:
        raise ModelArtifactError("The classifier returned an unsupported legal category.")

    probability: float | None = None
    probability_method = getattr(classifier, "predict_proba", None)
    if callable(probability_method):
        try:
            class_labels = list(classifier.classes_)
            prediction_index = class_labels.index(prediction)
            probability = float(probability_method(features)[0][prediction_index])
        except Exception:
            probability = None

    return str(prediction), probability


def predict_category(
    text: str,
    *,
    classifier: Any | None = None,
    vectorizer: Any | None = None,
    model_dir: str | Path = DEFAULT_MODEL_DIR,
) -> str:
    """Predict one supported category using the fitted training vectorizer."""

    category, _ = predict_category_with_confidence(
        text,
        classifier=classifier,
        vectorizer=vectorizer,
        model_dir=model_dir,
    )
    return category
