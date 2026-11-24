"""TF-IDF feature extraction shared by model training and inference."""

from __future__ import annotations

from collections.abc import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils.validation import check_is_fitted

from src.data_preprocessing import preprocess_text, tokenize_legal_text


class FeatureExtractionError(ValueError):
    """Raised when text cannot be represented by the configured vectorizer."""


def create_tfidf_vectorizer() -> TfidfVectorizer:
    """Create the project's legal-aware TF-IDF vectorizer.

    Stopword removal is disabled. Unigrams and bigrams retain useful legal
    phrases such as "shall not" while the custom tokenizer keeps section
    references together where possible.
    """

    return TfidfVectorizer(
        preprocessor=preprocess_text,
        tokenizer=tokenize_legal_text,
        token_pattern=None,
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )


def _validate_texts(texts: Iterable[str]) -> list[str]:
    values = list(texts)
    if not values:
        raise FeatureExtractionError("At least one document is required for TF-IDF processing.")
    if any(not isinstance(text, str) or not text.strip() for text in values):
        raise FeatureExtractionError("TF-IDF input must contain non-empty text strings only.")
    return values


def fit_tfidf_vectorizer(texts: Iterable[str]) -> tuple[TfidfVectorizer, object]:
    """Fit a new vectorizer and transform texts; call only with training data."""

    values = _validate_texts(texts)
    vectorizer = create_tfidf_vectorizer()
    try:
        features = vectorizer.fit_transform(values)
    except ValueError as error:
        raise FeatureExtractionError("The training text produced no usable TF-IDF vocabulary.") from error
    return vectorizer, features


def transform_texts(vectorizer: TfidfVectorizer, texts: Iterable[str]) -> object:
    """Transform text with an already-fitted vectorizer without refitting it."""

    values = _validate_texts(texts)
    try:
        check_is_fitted(vectorizer, attributes=("vocabulary_", "idf_"))
        return vectorizer.transform(values)
    except FeatureExtractionError:
        raise
    except Exception as error:
        raise FeatureExtractionError("Could not transform text with the fitted TF-IDF vectorizer.") from error
