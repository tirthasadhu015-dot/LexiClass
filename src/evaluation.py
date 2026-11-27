"""Evaluate saved candidate models on the original held-out test split."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from src.dataset_validation import LEGAL_CATEGORIES, load_and_validate_dataset
from src.data_preprocessing import preprocess_text
from src.model_training import (
    DEFAULT_DATASET_PATH,
    DEFAULT_MODEL_DIR,
    DEFAULT_RANDOM_STATE,
    DEFAULT_TEST_SIZE,
    MIN_SAMPLES_PER_CATEGORY,
    DatasetTrainingError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports" / "evaluation"
SUPPORTED_MODELS = ("Logistic Regression", "Linear SVM")


class EvaluationUnavailableError(RuntimeError):
    """Raised when genuine held-out data or matching trained artifacts are missing."""


def _load_dataset_and_training_report(
    dataset_path: str | Path,
    model_dir: str | Path,
) -> tuple[list[str], list[str], dict[str, Any]]:
    dataframe, validation = load_and_validate_dataset(dataset_path)
    if validation.errors:
        raise EvaluationUnavailableError("Dataset validation failed: " + " ".join(validation.errors))
    if dataframe.empty:
        raise EvaluationUnavailableError(
            "The dataset contains 0 labeled records. Evaluation requires a genuine held-out test set."
        )

    labels = dataframe["category"].astype(str).str.strip().tolist()
    distribution = {category: labels.count(category) for category in LEGAL_CATEGORIES}
    missing = [category for category, count in distribution.items() if count == 0]
    if missing:
        raise EvaluationUnavailableError(
            "Evaluation requires every supported category. Missing: " + ", ".join(missing)
        )
    insufficient = {
        category: count
        for category, count in distribution.items()
        if count < MIN_SAMPLES_PER_CATEGORY
    }
    if insufficient:
        counts = "; ".join(f"{category}: {count}" for category, count in insufficient.items())
        raise EvaluationUnavailableError(
            f"At least {MIN_SAMPLES_PER_CATEGORY} records per category are required by the training split. "
            f"Current counts: {counts}."
        )

    training_report_path = Path(model_dir) / "evaluation_report.json"
    if not training_report_path.is_file():
        raise EvaluationUnavailableError(
            "Training metadata is missing. Train both candidates and save the held-out split metadata first."
        )
    try:
        training_report = json.loads(training_report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationUnavailableError("Saved training metadata could not be read.") from error

    dataset_hash = hashlib.sha256(Path(dataset_path).read_bytes()).hexdigest()
    if training_report.get("dataset_sha256") != dataset_hash:
        raise EvaluationUnavailableError(
            "The dataset differs from the version used to train the saved models. Retrain before evaluation."
        )
    if training_report.get("scikit_learn_version") != sklearn.__version__:
        raise EvaluationUnavailableError(
            "The scikit-learn version differs from the training metadata. Retrain to reproduce the test split safely."
        )

    return (
        [preprocess_text(text) for text in dataframe["text"].astype(str)],
        labels,
        training_report,
    )


def _load_candidate_models(model_dir: str | Path, training_report: dict[str, Any]) -> tuple[Any, dict[str, Any], Any]:
    model_directory = Path(model_dir)
    vectorizer_path = model_directory / "tfidf_vectorizer.joblib"
    artifact_names = training_report.get("candidate_artifacts", {})
    missing = [name for name in SUPPORTED_MODELS if name not in artifact_names]
    if missing or not vectorizer_path.is_file():
        raise EvaluationUnavailableError(
            "Saved candidate models or fitted vectorizer are missing. Retrain with the current training pipeline."
        )

    try:
        vectorizer = joblib.load(vectorizer_path)
        candidates = {
            name: joblib.load(model_directory / artifact_names[name])
            for name in SUPPORTED_MODELS
        }
    except Exception as error:
        raise EvaluationUnavailableError("One or more saved model artifacts could not be loaded.") from error

    deployed_classifier_path = model_directory / "classifier.joblib"
    if not deployed_classifier_path.is_file():
        raise EvaluationUnavailableError("The selected classifier artifact is missing; retrain the models.")
    try:
        deployed_classifier = joblib.load(deployed_classifier_path)
    except Exception as error:
        raise EvaluationUnavailableError("The selected classifier artifact could not be loaded.") from error
    return (vectorizer, candidates, deployed_classifier)


def _score_predictions(y_true: list[str], predictions: np.ndarray) -> dict[str, Any]:
    report = classification_report(
        y_true,
        predictions,
        labels=list(LEGAL_CATEGORIES),
        output_dict=True,
        zero_division=0,
    )
    report_text = classification_report(
        y_true,
        predictions,
        labels=list(LEGAL_CATEGORIES),
        target_names=list(LEGAL_CATEGORIES),
        zero_division=0,
    )
    per_category = {
        category: {
            "precision": float(report[category]["precision"]),
            "recall": float(report[category]["recall"]),
            "f1_score": float(report[category]["f1-score"]),
            "support": int(report[category]["support"]),
        }
        for category in LEGAL_CATEGORIES
    }
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision_macro": float(
            precision_score(y_true, predictions, labels=list(LEGAL_CATEGORIES), average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, predictions, labels=list(LEGAL_CATEGORIES), average="macro", zero_division=0)
        ),
        "f1_macro": float(
            f1_score(y_true, predictions, labels=list(LEGAL_CATEGORIES), average="macro", zero_division=0)
        ),
        "classification_report": per_category,
        "classification_report_text": report_text,
        "confusion_matrix": confusion_matrix(y_true, predictions, labels=list(LEGAL_CATEGORIES)).tolist(),
    }


def _plotting_libraries(output_dir: Path) -> tuple[Any, Any]:
    """Load headless plotting libraries with cache confined to report output."""

    cache_directory = output_dir / ".matplotlib"
    cache_directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_directory))
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as pyplot
    import seaborn

    return pyplot, seaborn

def _save_confusion_matrix(model_name: str, matrix: list[list[int]], output_dir: Path) -> Path:
    plt, sns = _plotting_libraries(output_dir)
    figure, axis = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        np.asarray(matrix),
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=LEGAL_CATEGORIES,
        yticklabels=LEGAL_CATEGORIES,
        ax=axis,
    )
    axis.set_title(f"{model_name} — Held-out Confusion Matrix")
    axis.set_xlabel("Predicted category")
    axis.set_ylabel("Actual category")
    figure.tight_layout()
    path = output_dir / ("confusion_matrix_" + model_name.lower().replace(" ", "_") + ".png")
    figure.savefig(path, dpi=160)
    plt.close(figure)
    return path


def _save_metric_comparison(results: dict[str, dict[str, Any]], output_dir: Path) -> Path:
    plt, _ = _plotting_libraries(output_dir)
    metrics = ("accuracy", "precision_macro", "recall_macro", "f1_macro")
    frame = pd.DataFrame(
        {name: [results[name][metric] for metric in metrics] for name in SUPPORTED_MODELS},
        index=["Accuracy", "Macro precision", "Macro recall", "Macro F1"],
    )
    axis = frame.plot(kind="bar", figsize=(10, 6), ylim=(0, 1), rot=0)
    axis.set_ylabel("Score")
    axis.set_title("Model Comparison on Held-out Test Data")
    axis.legend(title="Classifier")
    axis.grid(axis="y", alpha=0.25)
    figure = axis.get_figure()
    figure.tight_layout()
    path = output_dir / "model_metric_comparison.png"
    figure.savefig(path, dpi=160)
    plt.close(figure)
    return path


def _save_class_distribution(training_counts: dict[str, int], output_dir: Path) -> Path:
    plt, sns = _plotting_libraries(output_dir)
    frame = pd.DataFrame(
        {"Category": list(training_counts), "Training records": list(training_counts.values())}
    )
    figure, axis = plt.subplots(figsize=(10, 6))
    sns.barplot(data=frame, x="Category", y="Training records", color="#2563EB", ax=axis)
    axis.set_title("Training Set Class Distribution")
    axis.tick_params(axis="x", rotation=20)
    figure.tight_layout()
    path = output_dir / "training_class_distribution.png"
    figure.savefig(path, dpi=160)
    plt.close(figure)
    return path


def evaluate_models(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    model_dir: str | Path = DEFAULT_MODEL_DIR,
    report_dir: str | Path = DEFAULT_REPORT_DIR,
) -> dict[str, Any]:
    """Re-evaluate saved classifiers on the unchanged held-out test split."""

    texts, labels, training_report = _load_dataset_and_training_report(dataset_path, model_dir)
    split = training_report.get("split", {})
    test_size = split.get("test_size", DEFAULT_TEST_SIZE)
    random_state = split.get("random_state", DEFAULT_RANDOM_STATE)
    if not split.get("stratified"):
        raise EvaluationUnavailableError("Saved training metadata does not describe a stratified test split.")
    if training_report.get("sample_count") != len(texts):
        raise EvaluationUnavailableError("Dataset row count differs from saved training metadata; retrain first.")

    try:
        x_train, x_test, y_train, y_test = train_test_split(
            texts,
            labels,
            test_size=test_size,
            random_state=random_state,
            stratify=labels,
        )
    except ValueError as error:
        raise EvaluationUnavailableError(f"Could not recreate the stratified test split: {error}") from error
    if len(x_test) != training_report.get("test_count"):
        raise EvaluationUnavailableError("Could not reproduce the original test split; retrain before evaluation.")

    vectorizer, candidates, deployed_classifier = _load_candidate_models(model_dir, training_report)
    try:
        test_features = vectorizer.transform(x_test)
        predictions = {name: model.predict(test_features) for name, model in candidates.items()}
        selected_name = training_report.get("selected_model")
        if selected_name not in candidates:
            raise EvaluationUnavailableError("Training metadata names an unsupported selected model.")
        selected_deployed_predictions = deployed_classifier.predict(test_features)
        if not np.array_equal(selected_deployed_predictions, predictions[selected_name]):
            raise EvaluationUnavailableError("Selected model artifact does not match its saved comparison candidate.")
    except EvaluationUnavailableError:
        raise
    except Exception as error:
        raise EvaluationUnavailableError("Could not generate predictions for the held-out test split.") from error

    results = {name: _score_predictions(y_test, values) for name, values in predictions.items()}
    training_counts = {category: y_train.count(category) for category in LEGAL_CATEGORIES}
    nonzero_counts = [count for count in training_counts.values() if count > 0]
    imbalance_ratio = max(nonzero_counts) / min(nonzero_counts) if nonzero_counts else None
    imbalance_threshold = 1.5
    report = {
        "dataset_path": str(Path(dataset_path)),
        "dataset_sha256": training_report["dataset_sha256"],
        "model_artifact_sha256": {
            "classifier": hashlib.sha256((Path(model_dir) / "classifier.joblib").read_bytes()).hexdigest(),
            "vectorizer": hashlib.sha256((Path(model_dir) / "tfidf_vectorizer.joblib").read_bytes()).hexdigest(),
        },
        "scikit_learn_version": sklearn.__version__,
        "dataset_records": len(texts),
        "training_records": len(x_train),
        "test_records": len(x_test),
        "training_class_distribution": training_counts,
        "test_class_distribution": {category: y_test.count(category) for category in LEGAL_CATEGORIES},
        "class_imbalance": {
            "training_max_to_min_ratio": imbalance_ratio,
            "possible_imbalance_flag": bool(imbalance_ratio is not None and imbalance_ratio >= imbalance_threshold),
            "flag_threshold_ratio": imbalance_threshold,
            "note": "The ratio is a screening heuristic; review category sources and sampling before modeling.",
        },
        "selected_model": selected_name,
        "selection_basis": training_report.get("selection_metric"),
        "models": results,
    }

    output_directory = Path(report_dir)
    output_directory.mkdir(parents=True, exist_ok=True)
    figure_paths = {
        name: str(_save_confusion_matrix(name, result["confusion_matrix"], output_directory))
        for name, result in results.items()
    }
    figure_paths["metric_comparison"] = str(_save_metric_comparison(results, output_directory))
    figure_paths["training_class_distribution"] = str(_save_class_distribution(training_counts, output_directory))
    report["figures"] = figure_paths

    (output_directory / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (output_directory / "model_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("model", "accuracy", "precision_macro", "recall_macro", "f1_macro"))
        for name in SUPPORTED_MODELS:
            writer.writerow((name, *(results[name][metric] for metric in ("accuracy", "precision_macro", "recall_macro", "f1_macro"))))
    report_text = "\n\n".join(
        f"{name}\n{'=' * len(name)}\n{results[name]['classification_report_text']}"
        for name in SUPPORTED_MODELS
    )
    (output_directory / "classification_report.txt").write_text(report_text, encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate saved LexiClass AI classifiers on the held-out test set.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH, help="Original training CSV")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Trained model artifact directory")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR, help="Evaluation output directory")
    args = parser.parse_args()
    try:
        report = evaluate_models(args.dataset, args.model_dir, args.report_dir)
    except (EvaluationUnavailableError, DatasetTrainingError, OSError) as error:
        parser.exit(2, f"Evaluation unavailable: {error}\n")

    print(f"Evaluated {report['test_records']} held-out records from {report['dataset_records']} dataset records.")
    print(f"Selected model: {report['selected_model']}")
    for name in SUPPORTED_MODELS:
        metrics = report["models"][name]
        print(
            f"{name}: accuracy={metrics['accuracy']:.4f}, "
            f"precision_macro={metrics['precision_macro']:.4f}, "
            f"recall_macro={metrics['recall_macro']:.4f}, f1_macro={metrics['f1_macro']:.4f}"
        )
    print(f"Reports and figures saved to {args.report_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
