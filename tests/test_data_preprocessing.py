"""Tests for conservative legal text preprocessing."""

from __future__ import annotations

import unittest

from src.data_preprocessing import (
    PROTECTED_LEGAL_TOKENS,
    normalize_legal_text,
    preprocess_text,
    remove_stop_words,
    tokenize_legal_text,
)


class LegalTextPreprocessingTests(unittest.TestCase):
    def test_normalizes_formatting_without_changing_legal_meaning(self) -> None:
        text = (
            "  WHEREAS,\u00a0the tenant shall not waive any right\u00ad\r\n"
            "\r\n\r\nunless notice is given without prejudice.\u200b  "
        )
        self.assertEqual(
            normalize_legal_text(text),
            "WHEREAS, the tenant shall not waive any right\n\nunless notice is given without prejudice.",
        )

    def test_preserves_case_punctuation_citations_and_paragraphs_by_default(self) -> None:
        text = "Article 21: No person shall be deprived of liberty.\n\nSection 420A(2) applies."
        self.assertEqual(preprocess_text(text), text)

    def test_tokenizer_keeps_negations_and_legal_references(self) -> None:
        tokens = tokenize_legal_text(
            "The claim is not barred unless Section 420A(2) and \u00a7 302/34 apply."
        )
        self.assertIn("not", tokens)
        self.assertIn("unless", tokens)
        self.assertIn("420A(2)", tokens)
        self.assertIn("\u00a7 302/34", tokens)

    def test_stopword_filter_preserves_negations_and_legal_terms(self) -> None:
        tokens = ["The", "claim", "is", "not", "barred", "unless", "notice", "is", "given"]
        result = remove_stop_words(tokens, {"the", "is", "not", "unless", "barred"})
        self.assertEqual(result, ["claim", "not", "unless", "notice", "given"])
        self.assertTrue(PROTECTED_LEGAL_TOKENS.issuperset({"not", "unless", "without"}))

    def test_preprocess_uses_optional_stopwords_only_when_requested(self) -> None:
        text = "The party shall not act unless notice is given."
        result = preprocess_text(text, stop_words={"the", "party", "shall", "not", "unless", "is"})
        self.assertEqual(result, "shall not act unless notice given")

    def test_handles_empty_and_none_input(self) -> None:
        self.assertEqual(preprocess_text("   \r\n\t  "), "")
        self.assertEqual(preprocess_text(None), "")
        self.assertEqual(tokenize_legal_text(None), [])

    def test_rejects_invalid_input_types(self) -> None:
        with self.assertRaises(TypeError):
            normalize_legal_text(42)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            remove_stop_words(["word"], "word")

    def test_does_not_lemmatize_or_aggressively_clean(self) -> None:
        text = "The parties' agreements were not valid unless signed."
        self.assertEqual(preprocess_text(text), text)


if __name__ == "__main__":
    unittest.main()
