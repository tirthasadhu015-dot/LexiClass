"""Streamlit integration tests for uploads when no trained model is present."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import unittest

from docx import Document
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from streamlit.testing.v1 import AppTest


LEGAL_TEXT = "Section 12: The claim shall not be waived without written consent."
APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def make_docx(*, include_text: bool = True) -> bytes:
    document = Document()
    if include_text:
        document.add_paragraph(LEGAL_TEXT)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def make_pdf() -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_reference = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_reference})}
    )
    content = DecodedStreamObject()
    content.set_data(f"BT /F1 12 Tf 30 250 Td ({LEGAL_TEXT}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(content)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class StreamlitUploadIntegrationTests(unittest.TestCase):
    def upload_on_classification_page(self, filename: str, content: bytes, mime_type: str):
        app = AppTest.from_file(str(APP_PATH)).run(timeout=10)
        app.radio[0].set_value("Classify Document").run(timeout=10)
        app.file_uploader[0].set_value((filename, content, mime_type)).run(timeout=10)
        return app

    def test_pdf_upload_extracts_text_in_the_streamlit_page(self) -> None:
        app = self.upload_on_classification_page("case.pdf", make_pdf(), "application/pdf")

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.text_area), 1)
        self.assertIn("shall not be waived", app.text_area[0].value)
        self.assertTrue(any("Classification is unavailable" in item.value for item in app.info))

    def test_docx_upload_extracts_text_in_the_streamlit_page(self) -> None:
        app = self.upload_on_classification_page(
            "agreement.docx",
            make_docx(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.text_area), 1)
        self.assertIn("shall not be waived", app.text_area[0].value)

    def test_empty_docx_upload_shows_error_without_crashing(self) -> None:
        app = self.upload_on_classification_page(
            "empty.docx",
            make_docx(include_text=False),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        self.assertEqual(len(app.exception), 0)
        self.assertGreaterEqual(len(app.error), 1)
        self.assertEqual(len(app.text_area), 0)

    def test_legal_knowledge_base_page_renders_without_breaking_classification_pages(self) -> None:
        app = AppTest.from_file(str(APP_PATH)).run(timeout=10)
        app.radio[0].set_value("Legal Knowledge Base").run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any(title.value == "Legal Knowledge Base" for title in app.title))
        self.assertTrue(any("not legal advice" in item.value.lower() for item in app.warning))


if __name__ == "__main__":
    unittest.main()
