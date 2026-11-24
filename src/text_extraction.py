"""Safe, in-memory text extraction for PDF and DOCX uploads."""

from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Final

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from pypdf import PdfReader


MAX_UPLOAD_SIZE_BYTES: Final = 20 * 1024 * 1024
MAX_DOCX_UNCOMPRESSED_SIZE_BYTES: Final = 100 * 1024 * 1024
MAX_DOCX_ARCHIVE_MEMBERS: Final = 1_000
SUPPORTED_EXTENSIONS: Final = {".pdf", ".docx"}


class DocumentExtractionError(ValueError):
    """Base exception for document validation and extraction failures."""


class UnsupportedFileTypeError(DocumentExtractionError):
    """Raised when a document extension is not supported."""


class DocumentTooLargeError(DocumentExtractionError):
    """Raised when the document exceeds the configured size limit."""


class EmptyDocumentError(DocumentExtractionError):
    """Raised when a document has no extractable text."""


class UnreadableDocumentError(DocumentExtractionError):
    """Raised when a document is corrupt, encrypted, or otherwise unreadable."""


def normalize_extracted_text(text: str) -> str:
    """Normalize line endings and excess horizontal/blank whitespace.

    Paragraph and line boundaries are retained so section numbering and the
    document's basic layout remain useful to downstream NLP processing.
    """

    normalized_lines = [
        re.sub(r"[\t\f\v ]+", " ", line).strip()
        for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ]
    while normalized_lines and not normalized_lines[0]:
        normalized_lines.pop(0)
    while normalized_lines and not normalized_lines[-1]:
        normalized_lines.pop()

    compact_lines: list[str] = []
    blank_line_added = False
    for line in normalized_lines:
        if line:
            compact_lines.append(line)
            blank_line_added = False
        elif compact_lines and not blank_line_added:
            compact_lines.append("")
            blank_line_added = True

    return "\n".join(compact_lines)


def _extract_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content), strict=False)
        if reader.is_encrypted:
            raise UnreadableDocumentError("Encrypted PDF files are not supported.")
        page_text = [page.extract_text() or "" for page in reader.pages]
    except DocumentExtractionError:
        raise
    except Exception as error:
        raise UnreadableDocumentError("The PDF is corrupted or could not be read.") from error

    text = normalize_extracted_text("\n\n".join(page_text))
    if not text:
        raise EmptyDocumentError(
            "The PDF contains no extractable text. Scanned PDFs require OCR, which is not supported yet."
        )
    return text


def _validate_docx_archive(content: bytes) -> None:
    """Reject suspiciously large or encrypted DOCX ZIP containers before parsing."""

    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            members = archive.infolist()
            if len(members) > MAX_DOCX_ARCHIVE_MEMBERS:
                raise UnreadableDocumentError("The DOCX package contains too many parts to process safely.")
            if any(member.flag_bits & 0x1 for member in members):
                raise UnreadableDocumentError("Encrypted DOCX packages are not supported.")
            total_uncompressed_size = sum(member.file_size for member in members)
            if total_uncompressed_size > MAX_DOCX_UNCOMPRESSED_SIZE_BYTES:
                raise DocumentTooLargeError("The uncompressed DOCX content exceeds the processing size limit.")
    except DocumentExtractionError:
        raise
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as error:
        raise UnreadableDocumentError("The DOCX file is corrupted or is not a valid DOCX package.") from error


def _extract_docx(content: bytes) -> str:
    _validate_docx_archive(content)
    try:
        document = Document(BytesIO(content))
        content_blocks: list[str] = []
        for element in document.element.body.iterchildren():
            if isinstance(element, CT_P):
                paragraph = Paragraph(element, document)
                if paragraph.text.strip():
                    content_blocks.append(paragraph.text)
            elif isinstance(element, CT_Tbl):
                table = Table(element, document)
                for row in table.rows:
                    cells = [cell.text for cell in row.cells]
                    if any(cell.strip() for cell in cells):
                        content_blocks.append(" | ".join(cells))
    except DocumentExtractionError:
        raise
    except Exception as error:
        raise UnreadableDocumentError("The DOCX file is corrupted or could not be read.") from error

    text = normalize_extracted_text("\n\n".join(content_blocks))
    if not text:
        raise EmptyDocumentError("The DOCX file contains no extractable text.")
    return text


def extract_text(
    file_name: str,
    file_content: bytes | bytearray | memoryview,
    *,
    max_file_size_bytes: int = MAX_UPLOAD_SIZE_BYTES,
) -> str:
    """Extract normalized text from PDF/DOCX bytes without writing to disk.

    Args:
        file_name: Uploaded filename used only to validate its extension.
        file_content: File bytes supplied by the upload layer.
        max_file_size_bytes: Maximum compressed upload size (20 MiB by default).

    Returns:
        Extracted text with normalized whitespace and preserved line breaks.

    Raises:
        DocumentExtractionError: If the type, size, contents, or extracted text
            are invalid or unreadable.
    """

    if not isinstance(file_name, str) or not file_name.strip():
        raise UnsupportedFileTypeError("A filename with a .pdf or .docx extension is required.")

    extension = Path(file_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError("Only PDF and DOCX documents are supported.")

    if not isinstance(file_content, (bytes, bytearray, memoryview)):
        raise DocumentExtractionError("Document content must be provided as bytes.")
    if max_file_size_bytes <= 0:
        raise ValueError("max_file_size_bytes must be a positive integer.")
    if len(file_content) > max_file_size_bytes:
        raise DocumentTooLargeError("The uploaded file exceeds the configured size limit.")
    content = bytes(file_content)
    if not content:
        raise EmptyDocumentError("The uploaded file is empty.")

    if extension == ".pdf":
        return _extract_pdf(content)
    return _extract_docx(content)

