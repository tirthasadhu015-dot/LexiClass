"""Dataset preparation, model comparison, evaluation, and artifact saving."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.dataset_validation import LEGAL_CATEGORIES, load_and_validate_dataset
from src.feature_extraction import FeatureExtractionError, create_tfidf_vectorizer
from src.data_preprocessing import preprocess_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "dataset" / "legal_documents.csv"
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models"
MIN_SAMPLES_PER_CATEGORY = 10
DEFAULT_TEST_SIZE = 0.2
DEFAULT_CV_FOLDS = 5
DEFAULT_RANDOM_STATE = 42
CLASSIFIER_FILENAME = "classifier.joblib"
VECTORIZER_FILENAME = "tfidf_vectorizer.joblib"
EVALUATION_FILENAME = "evaluation_report.json"


class DatasetTrainingError(ValueError):
    """Raised when the available dataset cannot support valid model training."""


@dataclass(frozen=True)
class CandidateResult:
    """Cross-validation and held-out test results for one classifier."""

    cv_accuracy: float
    cv_precision_macro: float
    cv_recall_macro: float
    cv_f1_macro: float
    test_accuracy: float
    test_precision_macro: float
    test_recall_macro: float
    test_f1_macro: float
    per_class: dict[str, dict[str, float]]
    confusion_matrix: list[list[int]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "cross_validation": {
                "accuracy": self.cv_accuracy,
                "precision_macro": self.cv_precision_macro,
                "recall_macro": self.cv_recall_macro,
                "f1_macro": self.cv_f1_macro,
            },
            "held_out_test": {
                "accuracy": self.test_accuracy,
                "precision_macro": self.test_precision_macro,
                "recall_macro": self.test_recall_macro,
                "f1_macro": self.test_f1_macro,
                "per_class": self.per_class,
                "confusion_matrix": self.confusion_matrix,
            },
        }


@dataclass(frozen=True)
class TrainingResult:
    """Actual dataset, evaluation, selection, and output-file details."""

    sample_count: int
    training_count: int
    test_count: int
    class_distribution: dict[str, int]
    selected_model: str
    candidate_results: dict[str, CandidateResult]
    classifier_path: Path
    vectorizer_path: Path
    evaluation_path: Path


def _new_classifiers(random_state: int) -> dict[str, Any]:
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=2_000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "Linear SVM": LinearSVC(class_weight="balanced", random_state=random_state),
    }


def _prepare_dataset(dataset_path: str | Path) -> tuple[list[str], list[str], dict[str, int]]:
    dataframe, report = load_and_validate_dataset(dataset_path)
    if report.errors:
        raise DatasetTrainingError("Dataset validation failed: " + " ".join(report.errors))
    if dataframe.empty:
        raise DatasetTrainingError(
            f"Dataset has 0 labeled records at {Path(dataset_path)}. Add genuine, validated records before training."
        )

    labels = dataframe["category"].astype(str).str.strip()
    class_distribution = {
        category: int(labels.eq(category).sum())
        for category in LEGAL_CATEGORIES
    }
    missing_categories = [category for category, count in class_distribution.items() if count == 0]
    if missing_categories:
        raise DatasetTrainingError(
            "Training requires examples from all five supported categories. Missing: "
            + ", ".join(missing_categories)
            + f". Dataset currently contains {len(dataframe)} record(s)."
        )

    insufficient = {
        category: count
        for category, count in class_distribution.items()
        if count < MIN_SAMPLES_PER_CATEGORY
    }
    if insufficient:
        counts = "; ".join(f"{category}: {count}" for category, count in insufficient.items())
        raise DatasetTrainingError(
            f"At least {MIN_SAMPLES_PER_CATEGORY} records per category are required for the stratified holdout "
            f"and {DEFAULT_CV_FOLDS}-fold cross-validation. Current counts: {counts}."
        )

    texts = [preprocess_text(value) for value in dataframe["text"].astype(str)]
    if any(not text for text in texts):
        raise DatasetTrainingError("Dataset contains text that becomes empty after preprocessing.")
    return texts, labels.tolist(), class_distribution


def _cross_validation_scores(
    name: str,
    classifier: Any,
    texts: list[str],
    labels: list[str],
    *,
    random_state: int,
) -> dict[str, float]:
    pipeline = Pipeline(
        [
            ("tfidf", create_tfidf_vectorizer()),
            ("classifier", classifier),
        ]
    )
    folds = StratifiedKFold(n_splits=DEFAULT_CV_FOLDS, shuffle=True, random_state=random_state)
    scoring = {
        "accuracy": "accuracy",
        "precision_macro": "precision_macro",
        "recall_macro": "recall_macro",
        "f1_macro": "f1_macro",
    }
    try:
        scores = cross_validate(
            pipeline,
            texts,
            labels,
            cv=folds,
            scoring=scoring,
            n_jobs=1,
            error_score="raise",
        )
    except Exception as error:
        raise DatasetTrainingError(f"{name} cross-validation failed: {error}") from error
    return {metric: float(scores[f"test_{metric}"].mean()) for metric in scoring}


def train_and_evaluate(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    model_dir: str | Path = DEFAULT_MODEL_DIR,
    *,
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> TrainingResult:
    """Compare Logistic Regression and Linear SVM, then save the selected model.

    Vectorizers inside cross-validation are fitted only on each fold's training
    partition. The final vectorizer is fitted only on the training partition;
    the held-out test data is transformed with that already-fitted vectorizer.
    Model selection uses mean cross-validated macro F1, leaving the test split
    for final evaluation.
    """

    if not 0 < test_size < 1:
        raise ValueError("test_size must be greater than 0 and less than 1.")

    texts, labels, class_distribution = _prepare_dataset(dataset_path)
    try:
        x_train, x_test, y_train, y_test = train_test_split(
            texts,
            labels,
            test_size=test_size,
            random_state=random_state,
            stratify=labels,
        )
    except ValueError as error:
        raise DatasetTrainingError(f"Could not create a stratified train/test split: {error}") from error

    classifiers = _new_classifiers(random_state)
    cv_results = {
        name: _cross_validation_scores(name, classifier, x_train, y_train, random_state=random_state)
        for name, classifier in classifiers.items()
    }
    selected_name = max(
        classifiers,
        key=lambda name: (cv_results[name]["f1_macro"], cv_results[name]["accuracy"]),
    )

    # Fit one final vectorizer on training data only and reuse it for all final
    # classifiers and held-out transformation.
    vectorizer = create_tfidf_vectorizer()
    try:
        x_train_features = vectorizer.fit_transform(x_train)
        x_test_features = vectorizer.transform(x_test)
    except ValueError as error:
        raise DatasetTrainingError(f"TF-IDF feature extraction failed: {error}") from error

    fitted_classifiers: dict[str, Any] = {}
    results: dict[str, CandidateResult] = {}
    for name, classifier in classifiers.items():
        classifier.fit(x_train_features, y_train)
        predictions = classifier.predict(x_test_features)
        per_class_report = classification_report(
            y_test,
            predictions,
            labels=list(LEGAL_CATEGORIES),
            output_dict=True,
            zero_division=0,
        )
        per_class = {
            category: {
                metric: float(per_class_report[category][metric])
                for metric in ("precision", "recall", "f1-score", "support")
            }
            for category in LEGAL_CATEGORIES
        }
        results[name] = CandidateResult(
            cv_accuracy=cv_results[name]["accuracy"],
            cv_precision_macro=cv_results[name]["precision_macro"],
            cv_recall_macro=cv_results[name]["recall_macro"],
            cv_f1_macro=cv_results[name]["f1_macro"],
            test_accuracy=float(accuracy_score(y_test, predictions)),
            test_precision_macro=float(
                precision_score(y_test, predictions, labels=list(LEGAL_CATEGORIES), average="macro", zero_division=0)
            ),
            test_recall_macro=float(
                recall_score(y_test, predictions, labels=list(LEGAL_CATEGORIES), average="macro", zero_division=0)
            ),
            test_f1_macro=float(
                f1_score(y_test, predictions, labels=list(LEGAL_CATEGORIES), average="macro", zero_division=0)
            ),
            per_class=per_class,
            confusion_matrix=confusion_matrix(y_test, predictions, labels=list(LEGAL_CATEGORIES)).tolist(),
        )
        fitted_classifiers[name] = classifier

    output_directory = Path(model_dir)
    output_directory.mkdir(parents=True, exist_ok=True)
    classifier_path = output_directory / CLASSIFIER_FILENAME
    vectorizer_path = output_directory / VECTORIZER_FILENAME
    evaluation_path = output_directory / EVALUATION_FILENAME

    report = {
        "dataset_path": str(Path(dataset_path)),
        "sample_count": len(texts),
        "training_count": len(x_train),
        "test_count": len(x_test),
        "class_distribution": class_distribution,
        "split": {"test_size": test_size, "random_state": random_state, "stratified": True},
        "selection_metric": "mean 5-fold cross-validation macro F1",
        "selected_model": selected_name,
        "candidate_results": {name: result.as_dict() for name, result in results.items()},
    }

    joblib.dump(fitted_classifiers[selected_name], classifier_path)
    joblib.dump(vectorizer, vectorizer_path)
    evaluation_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return TrainingResult(
        sample_count=len(texts),
        training_count=len(x_train),
        test_count=len(x_test),
        class_distribution=class_distribution,
        selected_model=selected_name,
        candidate_results=results,
        classifier_path=classifier_path,
        vectorizer_path=vectorizer_path,
        evaluation_path=evaluation_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Train and evaluate LexiClass AI text classifiers.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH, help="Labeled CSV dataset path")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Output directory for model artifacts")
    parser.add_argument("--test-size", type=float, default=DEFAULT_TEST_SIZE, help="Fraction held out for final testing")
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE, help="Reproducible split/CV seed")
    args = parser.parse_args()

    try:
        result = train_and_evaluate(
            args.dataset,
            args.model_dir,
            test_size=args.test_size,
            random_state=args.random_state,
        )
    except (DatasetTrainingError, FeatureExtractionError, OSError) as error:
        parser.exit(2, f"Training stopped: {error}\n")

    print(f"Dataset records: {result.sample_count} (train={result.training_count}, test={result.test_count})")
    print("Class distribution:")
    for category, count in result.class_distribution.items():
        print(f"  {category}: {count}")
    print(f"Selected model by cross-validated macro F1: {result.selected_model}")
    for name, metrics in result.candidate_results.items():
        print(
            f"{name}: CV macro F1={metrics.cv_f1_macro:.4f}; "
            f"test accuracy={metrics.test_accuracy:.4f}; "
            f"test macro F1={metrics.test_f1_macro:.4f}"
        )
    print(f"Saved classifier: {result.classifier_path}")
    print(f"Saved vectorizer: {result.vectorizer_path}")
    print(f"Saved evaluation report: {result.evaluation_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
