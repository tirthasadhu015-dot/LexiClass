"""Conservative preprocessing utilities for legal document text."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable


# Preserve legal references, numeric citations, and hyphenated legal terminology.
LEGAL_TOKEN_PATTERN = re.compile(
    r"\u00a7{1,2}\s*\d+[A-Za-z]?(?:[./:-]\d+[A-Za-z]?)*(?:\([A-Za-z0-9]+\))*"
    r"|\d+[A-Za-z]?(?:[./:-]\d+[A-Za-z]?)*(?:\([A-Za-z0-9]+\))*"
    r"|[^\W\d_]+(?:['\u2019][^\W\d_]+)*(?:[-\u2010-\u2015][^\W\d_]+(?:['\u2019][^\W\d_]+)*)*",
    re.UNICODE,
)

PROTECTED_LEGAL_TOKENS = frozenset(
    {
        "not", "no", "nor", "never", "neither", "unless", "without",
        "except", "notwithstanding", "shall", "must", "may", "cannot",
        "herein", "hereby", "thereof", "therein", "whereas",
    }
)

_ZERO_WIDTH_FORMATTING = ("\u200b", "\u200c", "\u200d", "\ufeff")


def normalize_legal_text(text: str | None) -> str:
    """Normalize formatting artifacts while preserving legal wording/layout.

    Capitalization, punctuation, numbers, citations, and paragraph boundaries
    are retained. The function does not lowercase, stem, remove punctuation,
    or de-hyphenate line endings.
    """

    if text is None:
        return ""
    if not isinstance(text, str):
        raise TypeError("Legal text must be a string or None.")

    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace("\u00a0", " ").replace("\u00ad", "")
    for formatting_character in _ZERO_WIDTH_FORMATTING:
        normalized = normalized.replace(formatting_character, "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace("\f", "\n").replace("\u2028", "\n").replace("\u2029", "\n")

    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in normalized.split("\n")]
    compact_lines: list[str] = []
    blank_line_added = False
    for line in lines:
        if line:
            compact_lines.append(line)
            blank_line_added = False
        elif compact_lines and not blank_line_added:
            compact_lines.append("")
            blank_line_added = True

    while compact_lines and not compact_lines[-1]:
        compact_lines.pop()
    return "\n".join(compact_lines)


def tokenize_legal_text(text: str | None) -> list[str]:
    """Split text into words and legal reference tokens without stopword removal."""

    return LEGAL_TOKEN_PATTERN.findall(normalize_legal_text(text))


def remove_stop_words(
    tokens: Iterable[str],
    stop_words: Iterable[str] | None = None,
) -> list[str]:
    """Remove caller-selected stop words while protecting legal terms.

    No built-in English stopword list is used. Review custom stopword choices
    against the legal corpus and keep options identical in training/inference.
    """

    token_list = list(tokens)
    if any(not isinstance(token, str) for token in token_list):
        raise TypeError("Tokens must contain only strings.")
    if stop_words is None:
        return token_list
    if isinstance(stop_words, str):
        raise TypeError("stop_words must be an iterable of words, not a single string.")

    stop_set: set[str] = set()
    for word in stop_words:
        if not isinstance(word, str):
            raise TypeError("Stop words must contain only strings.")
        cleaned_word = word.casefold().strip()
        if cleaned_word:
            stop_set.add(cleaned_word)

    return [
        token
        for token in token_list
        if token.casefold() not in stop_set or token.casefold() in PROTECTED_LEGAL_TOKENS
    ]


def preprocess_text(
    text: str | None,
    *,
    stop_words: Iterable[str] | None = None,
) -> str:
    """Prepare text consistently for both training and inference.

    Defaults to formatting normalization only. Optional stopword filtering
    tokenizes and returns space-separated tokens, retaining protected terms.
    """

    normalized = normalize_legal_text(text)
    if not normalized or stop_words is None:
        return normalized

    selected_stop_words = tuple(stop_words)
    if not selected_stop_words:
        return normalized
    filtered_tokens = remove_stop_words(tokenize_legal_text(normalized), selected_stop_words)
    return " ".join(filtered_tokens)
