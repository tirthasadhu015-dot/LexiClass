"""Unit tests for legal document text extraction."""

from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from docx import Document

from src.text_extraction import (
    DocumentTooLargeError,
    EmptyDocumentError,
    UnreadableDocumentError,
    UnsupportedFileTypeError,
    extract_text,
    normalize_extracted_text,
)


class TextExtractionTests(unittest.TestCase):
    def make_docx(self, *, with_text: bool = True) -> bytes:
        document = Document()
        if with_text:
            document.add_paragraph("  Section 12:   The claim shall not be waived.  ")
            table = document.add_table(rows=1, cols=2)
            table.cell(0, 0).text = "Party A"
            table.cell(0, 1).text = "Party B"
        buffer = BytesIO()
        document.save(buffer)
        return buffer.getvalue()

    @patch("src.text_extraction.PdfReader")
    def test_extracts_pdf_pages_and_normalizes_whitespace(self, reader_mock) -> None:
        reader_mock.return_value = SimpleNamespace(
            is_encrypted=False,
            pages=[
                SimpleNamespace(extract_text=lambda: "  Section 12:   Notwithstanding this Act.  "),
                SimpleNamespace(extract_text=lambda: "The claim shall not be waived."),
            ],
        )

        result = extract_text("case.PDF", b"%PDF-test")

        self.assertEqual(
            result,
            "Section 12: Notwithstanding this Act.\n\nThe claim shall not be waived.",
        )

    def test_extracts_docx_paragraphs_and_table_text(self) -> None:
        result = extract_text("agreement.docx", self.make_docx())

        self.assertIn("Section 12: The claim shall not be waived.", result)
        self.assertIn("Party A | Party B", result)

    def test_rejects_unsupported_extension(self) -> None:
        with self.assertRaises(UnsupportedFileTypeError):
            extract_text("document.txt", b"text")

    def test_rejects_files_over_size_limit_before_parsing(self) -> None:
        with self.assertRaises(DocumentTooLargeError):
            extract_text("document.pdf", b"1234", max_file_size_bytes=3)

    def test_rejects_zero_byte_upload(self) -> None:
        with self.assertRaises(EmptyDocumentError):
            extract_text("document.pdf", b"")

    def test_reports_corrupt_pdf_without_exposing_parser_error(self) -> None:
        with patch("src.text_extraction.PdfReader", side_effect=ValueError("parser internals")):
            with self.assertRaisesRegex(UnreadableDocumentError, "PDF is corrupted"):
                extract_text("document.pdf", b"not a PDF")

    def test_reports_corrupt_docx(self) -> None:
        with self.assertRaisesRegex(UnreadableDocumentError, "DOCX file is corrupted"):
            extract_text("document.docx", b"not a DOCX package")

    def test_reports_empty_docx(self) -> None:
        with self.assertRaises(EmptyDocumentError):
            extract_text("empty.docx", self.make_docx(with_text=False))

    @patch("src.text_extraction.PdfReader")
    def test_reports_scanned_pdf_without_ocr(self, reader_mock) -> None:
        reader_mock.return_value = SimpleNamespace(
            is_encrypted=False,
            pages=[SimpleNamespace(extract_text=lambda: None)],
        )
        with self.assertRaisesRegex(EmptyDocumentError, "require OCR"):
            extract_text("scan.pdf", b"%PDF-test")

    def test_normalizer_preserves_paragraphs_and_collapses_excess_blank_lines(self) -> None:
        self.assertEqual(
            normalize_extracted_text("\r\n Section 1:\tText \r\n\r\n\r\nSection 2: Text \r\n"),
            "Section 1: Text\n\nSection 2: Text",
        )


if __name__ == "__main__":
    unittest.main()

