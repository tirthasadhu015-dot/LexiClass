# LexiClass AI Dataset Guide

This directory is for genuine, legally usable legal-document text and its manually reviewed category labels. The project does not include a dataset yet. Do not place generated or synthetic legal documents in the training CSV.

## Directory layout

```text
dataset/
|-- raw/                 # Original files only when their storage is permitted
|-- processed/           # Extracted/normalized working text; not training labels
|-- annotations/         # Label review notes and adjudication records
|-- legal_documents.csv  # One final reviewed row per document
|-- source_register.csv  # Dataset-level source and rights register
`-- README.md
```

The CSVs are currently header-only. The `.gitkeep` files only preserve the empty folders. Keep downloaded source corpora out of this repository unless their terms explicitly permit redistribution; the folders are ignored by Git except for these placeholders.

## `legal_documents.csv` schema

The header is:

```text
document_id,document_title,text,category,source,source_url,license,language
```

Each row represents one original legal document, not a paragraph, chunk, or question-answer pair.

| Column | Required content |
|---|---|
| `document_id` | Stable unique ID from the source or a locally assigned non-sensitive ID. |
| `document_title` | Title as shown by the source. |
| `text` | Readable full-document text, preserving sections, citations, and negations. |
| `category` | Exactly one of the five approved labels after human review. |
| `source` | `source_id` from `source_register.csv`, or a precise source citation. |
| `source_url` | Direct document URL where available. If absent, source attribution must still resolve through `source` and the register. |
| `license` | Exact license/terms identifier applicable to this material; do not use a guessed license. |
| `language` | Language of the document, preferably an ISO 639-1 code such as `en` or `hi`. |

`source_register.csv` records one entry per collection/source. Its columns are `source_id`, `source_name`, `source_url`, `dataset_version`, `format`, `license`, `license_url`, `terms_url`, `accessed_on`, `attribution`, `usage_notes`, and `review_status`. Record the actual version and access date. Set `review_status` to a clear state such as `pending` or `approved`; do not train on sources whose rights have not been checked.

The validator requires all eight CSV columns and nonempty document ID, title, text, category, source, license, and language. A per-document URL can be blank when the source register still provides traceable attribution. Text shorter than 100 normalized characters is rejected for manual review; a short legal provision may be valid, but include it only after a reviewer confirms the content is complete and meaningful. If the threshold needs changing for a documented corpus, change `MIN_DOCUMENT_TEXT_CHARACTERS` in `src/dataset_validation.py` deliberately and record that decision.

## Collecting documents responsibly

1. Prefer official legislation, court, regulator, or publisher releases with terms that explicitly permit the intended collection and machine-learning use.
2. Read the dataset license, the originating document's terms, and any website/API terms. Public accessibility alone does not grant permission to scrape, redistribute, or train on the material.
3. Do not bypass access controls, forms, rate limits, robots directives, or other site restrictions. Do not scrape a website until its applicable terms have been checked.
4. Do not collect confidential, sealed, private, or unnecessary personal information. Minimize retained personal data and respect court redaction requirements.
5. Keep a source-register entry with the citation, version/date, direct source and license links, attribution requirements, and review decision. Preserve enough provenance to re-check each record later.
6. Store source originals in `raw/` only if the source terms permit local retention. Keep access-restricted originals out of Git. Store extracted text and annotation work in the corresponding working folders.
7. Add only one final document record to `legal_documents.csv` after the text, rights, and label have been reviewed. Do not silently infer labels from court, document type, authority, or case outcome.

### Extract PDF and DOCX text

Use the project's in-memory extraction module on a permitted local file:

```python
from pathlib import Path
from src.text_extraction import extract_text

path = Path("dataset/raw/source-document.pdf")  # or a .docx file
text = extract_text(path.name, path.read_bytes())
```

The extractor supports text-based PDF and DOCX, normalizes whitespace, and applies a 20 MiB input limit. Scanned PDFs without an embedded text layer need OCR, which is not implemented. Treat parser errors and no-text results as manual-review cases; do not substitute OCR or generated text without documenting and validating that process.

Record the extracted, reviewed text in the `text` column. Preserve legal meaning: do not remove words such as “not”, “unless”, or “without”, section references, citations, or material paragraph boundaries. Keep the source file's title, stable identifier, provenance, license, and language with the row.

## Labeling rules

Assign one primary category based on the document's central legal issue, operative rights/duties, and substantive subject. Read enough of the document to understand its purpose. A label is an annotation judgment, not a direct copy of court, document-type, or outcome metadata.

1. **Criminal Law** — criminal offenses, prosecution, criminal procedure, sentencing, or criminal liability is the central subject.
2. **Constitutional Law** — interpretation/application of a constitution, constitutional powers, fundamental rights, or constitutional validity is central.
3. **Property Law** — ownership/title, transfer, possession, lease, land, or other property rights are the central issue.
4. **Civil Law** — a civil dispute or private legal relationship is central and is not more specifically about constitutional or property law under these rules.
5. **Other Legal Domains** — the central subject is another legal domain (for example, tax, labor, intellectual property, or administrative regulation) and none of the four named categories is the best primary fit.

The list above is not a validated mapping from Indian court names, document types, or outcomes. A criminal court may issue an order concerning constitutional rights; a statute may cover several domains; and an outcome such as “allowed” does not determine the legal category. Never assign a label solely from those fields.

When two or more domains are genuinely central, the document is incomplete, or reasonable reviewers disagree, **do not choose a convenient label**. Record the candidate labels, rationale, reviewer, and status in annotation notes under `annotations/`; mark it `pending_manual_review` and keep it out of the final CSV until a qualified reviewer adjudicates it. “Other Legal Domains” is not a catch-all for uncertainty. Preserve the decision and rationale so a later reviewer can reproduce it.

## Duplicate and quality checks

- Keep source IDs where available; the validator rejects repeated `document_id` values (case-insensitive).
- The validator rejects exact duplicate text after case-folding and whitespace normalization. It does not detect paraphrases, reprints with changed formatting, translated copies, or overlapping judgment extracts; compare titles, citations, source IDs, and text manually.
- Avoid treating multiple QA pairs, paragraphs, or chunks from one judgment as independent documents. If using derived records, keep the original judgment ID and prevent all its derivatives from crossing training/test partitions.
- Check that extraction includes the whole document and not only a headnote, first page, or search snippet. Review unusually short text and extraction artifacts before annotation.
- Review missing fields, duplicate warnings, language, category consistency, and the source license before a record is admitted. Resolve annotation disagreements before changing `category`.

## Validation

Run from the project root:

```powershell
.\.venv\Scripts\python.exe -m src.dataset_validation
```

The report lists counts for every category and checks required columns/values, missing text and labels, invalid categories, duplicate IDs/text, missing direct URLs, and unusually short text. Validation is read-only: it does not repair records or assign labels. Any errors must be corrected manually and then revalidated.

## Candidate source review

Reviewed 2026-11-24. These are source assessments, not downloads or approvals for use. Dataset descriptions and terms can change; re-check the linked release and underlying content terms before collection.

### KanoonGPT Indian Legal Documents

- **Format and fields:** The publisher describes a Parquet dataset with one row per document and fields including `doc_id`, `document_title`, `document_type`, `document_jurisdiction`, `issuing_authority`, `issue_date`, `short_description`, and `text`. Its card reports 35,851 documents. The public release says source URLs/internal scraping provenance are omitted, so document-level provenance may need additional work.
- **License/conditions:** The dataset card declares Apache-2.0 and asks users to cite the dataset. Independently check any upstream content terms and the current card before use; the release notes machine-extracted metadata and text artifacts.
- **Fit to LexiClass:** The card describes document-type/metadata fields, not the five LexiClass labels. Do not translate `document_type` or `document_jurisdiction` directly into legal categories. Manually review document content and adjudicate labels. Convert selected, reviewed rows from Parquet to this CSV schema; verify provenance since source URLs are absent.
- **Source:** [KanoonGPT dataset card](https://huggingface.co/datasets/KanoonGPT/indian-legal-documents).
- **Acquisition review:** Public Hugging Face repository; its file browser lists eight Parquet shards totaling about 471 MB (the first shard is listed as 56.8 MB). The repository page did not present a sign-in gate during review. Use the official [file listing](https://huggingface.co/datasets/KanoonGPT/indian-legal-documents/tree/main/data) and download only a shard you have reviewed; do not use an automated full-repository download. The stated format is Parquet, so convert a selected file to CSV or JSON before using the importer below. No account requirement was shown in the reviewed public pages; access can change. The modest first shard is still a subset, not evidence of balanced coverage.

### Open Justice India

- **Format and fields:** Open Justice India describes a continuing initiative covering court judgments/orders in PDF and text, structured case data, cause lists, hearing data, and Indic-language support. The initiative page does not define one downloadable, stable dataset schema or a single data release. It also points to other projects; for example, a linked High Court collection described there is a separate, very large (~1 TB) Dattam Labs release, not an Open Justice India dataset to download automatically.
- **License/conditions:** The project page does not specify a blanket license for collected court records. The linked `ecourts` repository is GPL-3.0 software for scraping; that code license does not grant rights to the data retrieved from eCourts. Check the target court/site terms and any dataset-specific license before collection. No scraping is authorized by this guide.
- **Fit to LexiClass:** Court judgments/orders may provide document text, but the project does not supply the five target labels as a ready annotation field. Obtain a concrete release and its schema/terms first, then extract text and manually label; do not map court, case type, or outcome without a validated scheme.
- **Sources:** [Open Justice India project](https://openjustice-in.github.io/) and [its eCourts scraper repository](https://github.com/openjustice-in/ecourts).
- **Acquisition review:** No official single downloadable package, stable record count/file size, complete schema, or corpus-wide data license was identified on the initiative page. The separately linked ~1 TB collection is not recommended for this prototype.

### IndicLegalQA

- **Format and fields:** Mendeley Data describes a JSON release of 10,000 question-answer pairs derived from 1,256 Supreme Court judgments, with case names and judgment dates. The description reports 538 criminal and 718 civil cases and says topics include constitutional matters, property disputes, criminal offenses, and procedural matters. The landing page does not document the complete JSON field schema or establish a one-row-per-full-document format; inspect the downloaded package manually before deciding how to use it.
- **License/conditions:** The Mendeley record lists CC BY 4.0 for the dataset. Preserve attribution and check the license plus the underlying judgment-source terms; a dataset license should not be assumed to independently clear every source document for redistribution.
- **Fit to LexiClass:** This is primarily a question-answering resource, not an already labeled five-class document corpus. QA pairs are not independent original documents. If the package contains full judgment text and usable domain labels, verify them and manually map/adjudicate; otherwise it is not directly suitable as training rows. Keep judgment IDs grouped to prevent leakage across splits.
- **Sources:** [IndicLegalQA Mendeley Data version 2](https://data.mendeley.com/datasets/gf8n8cnmvc/2) and its [dataset paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12166829/).
- **Acquisition review:** The Mendeley record provides a public versioned dataset page; its description identifies JSON and a 10,000-pair QA dataset, but a stable package size and complete schema were not verified in this review. Inspect the current version's files and terms before downloading. It is small by description, but not a full-document corpus with the five required labels.

### Recommendation and acquisition decision

For an academic prototype, KanoonGPT is the best of these three candidates for *document text* because its public release describes document-level text plus title and document metadata, and declares Apache-2.0. It is not ready-to-train: labels for the five categories are absent and document-level original URLs/provenance are omitted. Rights to upstream source documents also need review. Manually examine the source card and current license, then open the official file listing above and download a selected Parquet shard through the browser's file link. Place the original permitted file under `dataset/raw/`; record exact release/version, URL, access date, attribution, and rights review in `source_register.csv`. Convert the selected shard to CSV/JSON with a local Parquet reader such as pandas with a Parquet engine, without dropping any fields. Import is gated until the source register entry is marked `approved`.

IndicLegalQA is the smaller alternative for studying QA data, but its questions and answers must not be mistaken for separate source documents or LexiClass labels. Open Justice India is not a single licensed corpus. Neither should be imported as labeled examples without examining the actual package and terms.

## Inspecting and importing a source file

The importer accepts CSV, JSON, and Parquet (through `pyarrow`). `pyarrow` is listed in `requirements.txt`; install project dependencies inside the virtual environment, not globally. The inspector reports columns, inferred types, row count, per-column missing-value counts, up to five text lengths, non-text metadata fields, and up to 20 distinct values from fields whose names indicate labels/categories/classes or document types. It never prints document contents. For example, inspect a downloaded Parquet shard directly:

```powershell
.\.venv\Scripts\python.exe -m src.dataset_import inspect dataset/raw/train-00000.parquet
```

Create a local JSON config (keep it out of Git) after inspecting actual source fields. Do not copy guessed column names. Example *shape* only; replace every placeholder with verified values:

```json
{
  "source_id": "approved_source_register_id",
  "column_map": {
    "document_id": "source_id_field",
    "document_title": "source_title_field",
    "text": "source_text_field",
    "category": "reviewed_source_label_field",
    "source_url": "verified_document_url_field",
    "language": "verified_language_field"
  },
  "default_language": "",
  "records_key": null,
  "category_map": {},
  "mapping_basis": ""
}
```

With an empty `category_map`, every row is explicitly marked `REVIEW_REQUIRED`. Only configure exact source-label mappings after a human has validated that mapping; document that validation in `mapping_basis`. The importer will not infer categories from keywords, court, type, or outcome. It writes a separate staging CSV plus a JSON count report and refuses to overwrite either file:

```powershell
.\.venv\Scripts\python.exe -m src.dataset_import import `
  --input dataset/raw/train-00000.parquet `
  --config dataset/annotations/import-config.json `
  --source-register dataset/source_register.csv `
  --output dataset/processed/selected-source-import.csv `
  --report dataset/processed/selected-source-report.json
```

The source register entry must be marked `approved` and contain source name, URL, and license. Review every staged row and its `original_metadata`; resolve duplicates, incomplete text, and `REVIEW_REQUIRED` labels manually. Do not copy the staging file to `legal_documents.csv` until human review and the standard dataset validator pass. No source file has been downloaded or imported as part of this review; current corpus record count remains zero.

An invalid or unreadable Parquet file produces an error; if the Parquet engine is unavailable, the command reports that `pyarrow` is required and gives the virtual-environment install command. Import refuses an empty source, and configured source columns must exist in the inspected file. Before importing a KanoonGPT shard, inspect its current release card and underlying document terms, then record verified version, official URL, exact license and terms, required attribution, access date, and usage restrictions in the existing source register columns. Do not set `review_status` to `approved` until a human completes that rights review. Inspect actual Parquet column names first. Set `source_id` and exact source-field names for ID, title, text, and language in `dataset/annotations/import-config.json`. Do not map `document_type` to one of the five legal categories automatically; with an empty `category_map`, imported records remain `REVIEW_REQUIRED`. Only add exact source-label mappings after documenting a validated human rule in `mapping_basis`. The template intentionally has no approved source ID or category mappings.

## Adding genuine records

1. Confirm rights and add an approved source row to `source_register.csv`.
2. Obtain permitted original documents without scraping against terms; keep source references and IDs.
3. Extract readable text from PDF/DOCX and manually verify it is complete and faithful.
4. Create annotation notes and have a reviewer assign one primary category using the rules above. Leave ambiguous items out until adjudicated.
5. Append one CSV row per original document, recording all required fields and exact source/license details.
6. Run the validator, manually fix every reported issue, and review class counts and source licensing before any later training phase.
