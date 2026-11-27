# Project Updates

## 2026-11-24 — Phase 1: Project Setup

- Created the initial directory scaffold and Python module files.
- Added `requirements.txt`, `.gitignore`, and an initial `README.md` with Windows PowerShell setup instructions.
- No dataset or trained model was created.
- Dependencies have not been installed or import-tested.

## 2026-11-24 — Phase 2: Dataset Preparation

- Added a header-only `dataset/legal_documents.csv` template with record text, category, and provenance fields; it contains no sample legal records.
- Added `src/dataset_validation.py` for required-field, category, duplicate, and class-distribution reporting.
- Updated the README, architecture, and project memory with the schema and validation usage.
- No external dataset was collected or added. The validation module has not been executed, so functional test results are not claimed.

## 2026-11-24 — Phase 3: Legal Document Text Extraction

- Added an in-memory PDF/DOCX extraction module with extension, size, empty-content, and unreadable-document handling.
- Added unit tests for PDF extraction (reader mocked), DOCX paragraphs/tables, whitespace normalization, invalid/oversized/empty files, corrupt files, and scanned-PDF no-text behavior.
- Documented the 20 MiB upload limit and the current lack of OCR support.
- Tests have not been run; no execution results are claimed.

## 2026-11-24 — Phase 4: NLP Text Preprocessing

- Implemented conservative legal-text normalization and tokenization in `src/data_preprocessing.py`.
- Added opt-in stopword removal with protected legal negations and selected legal terms; stemming and lemmatization remain disabled to avoid changing legal meaning.
- Added representative unit tests for legal clauses, citations, negations, whitespace artifacts, optional stopword handling, and invalid/empty input.
- Updated architecture, project memory, README, and task progress with the preprocessing decisions and test command.
- Tests have not been run; no execution results are claimed.

## 2026-11-24 — Phase 5: Feature Extraction and Model Training

- Added a reusable legal-aware TF-IDF vectorizer and separate training CLI/module for Logistic Regression and Linear SVM.
- Added stratified holdout and five-fold training-only model comparison; selection uses cross-validated macro F1, while the held-out split is reserved for final reporting.
- Added prediction helpers that load the saved classifier with its matching fitted vectorizer.
- Added tests for vectorizer reuse and the empty-dataset no-artifact guard; tests have not been run.
- Inspected `dataset/legal_documents.csv`: 0 data rows (header only). Executed `.venv/Scripts/python.exe train_model.py`; it stopped before training with the insufficient-data message. The `models/` directory still contains only `.gitkeep`; no model/vectorizer/metrics artifacts or performance scores were generated.


## 2026-11-24 — Phase 6: Machine Learning Model Evaluation

- Added `src/evaluation.py` and `evaluate_model.py` to recompute held-out metrics from saved candidate models and the unchanged training dataset.
- Added JSON/text/CSV evaluation outputs and Matplotlib/Seaborn figures for confusion matrices, metric comparison, and training class distribution; these are created only after real evaluation succeeds.
- Updated training provenance to record the dataset SHA-256 and scikit-learn version, and to retain both final candidate classifiers for reproducible comparison.
- Ran `.venv/Scripts/python.exe evaluate_model.py`; it stopped cleanly because the CSV has 0 labeled records. Confirmed `reports/evaluation/` was not created. The source dataset has 0 data rows and `models/` contains no trained artifacts, so no metrics or figures exist until genuine labeled data is prepared and models are trained.


## 2026-11-24 — Phase 7: Streamlit Web Application

- Replaced the setup-only entry point with a dashboard, document classification page, and About page using the documented legal-tech palette and responsive Streamlit layout.
- Added PDF/DOCX upload UI with filename/type/size details, extracted text display, loading/error states, in-memory handling, and a 20 MiB Streamlit server upload limit.
- Classification stays disabled until classifier and fitted vectorizer artifacts are available. Probability is displayed only when the loaded model provides `predict_proba`; dashboard accuracy is shown only when the evaluation report matches the current dataset and model artifacts.
- No model is available in the current project, so the app cannot yet produce genuine classification results. Integration and UI upload tests were subsequently run and are recorded below.


## 2026-11-24 - Integration: Application Workflow and Verification

- Connected prediction inference explicitly through `preprocess_text` and the shared `transform_texts` helper, which verifies and reuses the fitted TF-IDF vectorizer before classifier prediction.
- Added validation that model output belongs to one of the five supported legal categories; missing classifier/vectorizer artifacts and empty text have unit coverage.
- Added a safe top-level UI error boundary that logs unexpected rendering details server-side and shows a generic message to users.
- Added Streamlit upload integration tests for actual in-memory PDF and DOCX documents, alongside existing extraction, preprocessing, and feature-extraction tests. Added category-contract tests using mocked classifiers only; these do not create model files or produce application results.
- Ran `.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v`: all 34 tests passed. Streamlit AppTest emitted benign bare-mode `ScriptRunContext` warnings.
- The CSV remains header-only and `models/` contains no trained artifacts. Therefore a real classifier load, saved-model prediction, and full upload-to-real-prediction workflow cannot be verified until genuine labeled data is added and training succeeds.


## 2026-11-24 - Final Project Review

- Read all seven Markdown documents in `docs/` and reviewed the project tree, Python modules, tests, application entry point, dependency list, README, upload protections, and model/evaluation paths.
- Added `joblib` as an explicit dependency because prediction code imports it directly to load serialized artifacts.
- Verified `dataset/legal_documents.csv` has zero data rows and `models/` contains only `.gitkeep`. The dataset validator reports zero records in each supported category; evaluation exits because there is no held-out data. No dataset provenance, licenses, performance metrics, evaluation figures, or screenshots are present to report.
- Ran `.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v`: all 34 tests passed. `git diff --check` reports no whitespace errors (only Git line-ending notices).
- Started the app with `.venv/Scripts/python.exe -m streamlit run app.py --server.headless true`; Streamlit served the app at `http://localhost:8502`, then the process was stopped after the startup check. `pip check` reported no broken requirements.
- Expanded README with project architecture, actual dataset/evaluation status, absent screenshots, limitations, future work, and completed/partial/pending task status. No existing user files were removed.


## 2026-11-24 - Dataset Audit Before Model Training

- Inspected `dataset/`, `models/`, the dataset validator, training and feature-extraction code, and the relevant architecture, PRD, rules, memory, task, and update documentation.
- Verified `dataset/legal_documents.csv` is the only dataset file and contains the required columns `document_id`, `text`, `category`, `source`, `source_url`, and `license`, but has 0 data records. Validation reports 0 records for each of the five categories; missing values, duplicates, and invalid labels cannot occur in an empty dataset.
- Verified `models/` contains only `.gitkeep`; no existing working model or vectorizer was touched. The evaluator confirms it cannot run without held-out data. Training was not started.
- The current trainer requires all five categories and at least 10 valid records per category (50 records total minimum for its stratified holdout and five-fold CV), with nonempty unique document IDs/text, valid labels, and traceable `source`. Add only genuine documents with lawful use rights; record citation/collection in `source` and available URL and license terms in `source_url` and `license`.


## 2026-11-24 - Dataset Preparation

- Created `dataset/raw/`, `dataset/processed/`, and `dataset/annotations/`, preserving them with empty `.gitkeep` placeholders and keeping raw/working content ignored by Git.
- Updated `legal_documents.csv` to the requested eight-column, header-only schema and created header-only `source_register.csv` for source versions, licenses, terms, attribution, and review state.
- Added `dataset/README.md` with collection, extraction, labeling/adjudication, duplicate, provenance, validation, and source-review guidelines. No source corpus was downloaded and no legal records or labels were added.
- Reviewed official source pages for KanoonGPT Indian Legal Documents, Open Justice India, and IndicLegalQA. The guide records formats, fields, declared terms, category-fit gaps, provenance limitations, and the need to inspect source terms before use.
- Expanded `src/dataset_validation.py` for the new schema, required provenance/license values, duplicate checks, invalid categories, missing direct URL warnings, and short-text review errors. The validator remains read-only.
- Ran the dataset validator: 0 records in each category; template structurally valid but not training-ready. Ran the full unit suite: 41 tests passed. No model training was run and no model artifacts were modified.


## 2026-11-24 - Dataset Source Review and Import Pipeline

- Re-inspected the dataset templates and reviewed the source guidance. `dataset/legal_documents.csv` remains header-only; `dataset/source_register.csv` has no registered or approved source. No raw source file is present, and no genuine records have been imported.
- Reviewed the official KanoonGPT, Open Justice India, and IndicLegalQA release pages. The dataset guide records the verified release descriptions, available formats/metadata, declared license information, source-fit limitations, and official acquisition links. KanoonGPT is recommended for a manually labeled full-document prototype subset; it is not pre-labeled for LexiClass and no source was approved or downloaded.
- Added `src/dataset_import.py` for CSV/JSON field inspection and source-register-gated staging imports. It preserves original source fields in `original_metadata`, requires explicit category mappings with a written validation basis, marks unmapped labels `REVIEW_REQUIRED`, reports duplicates/incomplete/short records, and refuses to overwrite staging outputs. It does not write to the canonical training CSV or train a model.
- Updated `dataset/README.md` with the recommendation, manual acquisition notes, import configuration shape, and exact inspect/import commands.
- Verified importer inspection against the actual header-only template: 0 records and the eight expected schema columns. An initial full-suite attempt was blocked by the restricted workspace's lack of a writable temporary directory. After permission to use temporary files was granted, reran `.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v`: all 41 existing tests passed. Streamlit emitted bare-mode context warnings. The new importer has only had its inspect operation checked against the actual empty template; end-to-end import waits for an approved source and user-provided field mapping.
- Model training was not run. Current genuine dataset counts remain zero in all five categories; no source download, labels, model artifacts, or evaluation results were produced.


## 2026-11-24 - Parquet Inspection and Import Support

- Extended `src/dataset_import.py` to read CSV, JSON, and Parquet via `pyarrow`; added actionable missing-engine, unreadable/invalid Parquet, unsupported-format, missing-column, and empty-input errors.
- Expanded metadata-only inspection to report source columns and dtypes, row count, missing-value counts, up to five sample text lengths, metadata field names, and capped distinct values from likely label/category and document-type fields. Document text is not included in inspection output.
- Added `pyarrow` to `requirements.txt` and created the blank `dataset/annotations/import-config.json` template. Category mappings remain empty and the source register remains header-only/unapproved.
- Added isolated temporary-fixture tests covering Parquet inspection, explicit and missing field mappings, invalid categories, duplicate detection, empty Parquet input, missing Parquet engine, malformed Parquet, unmapped labels, and unsupported formats. Fixtures are created only in temporary directories, not `dataset/`.
- Ran targeted importer tests: 11 passed. Ran the full suite: 52 tests passed. Confirmed the actual canonical CSV still has 0 records; source register has no source entry; no external download or model training occurred.


## 2026-11-25 - Separate Legal Knowledge Base

- Inspected the existing UI and modules plus the required architecture, PRD, rules, and project memory. Verified `dataset/raw/indian_constitution.json` is a UTF-8 JSON list of 1,070 dictionaries with the ten expected fields. It contains IPC 575, Constitution of India 493, CrPC 1, and BNS 1 records. A second copy under `dataset/constitution/raw/` has the same SHA-256; processing uses the requested `dataset/raw/` path and leaves both sources unchanged.
- Added `src/legal_knowledge_base.py` to validate/normalize records, preserve the ten source fields and source URLs, report invalid/duplicate/incomplete records, create the separate reference CSV/report, and search by Act code, section, title/description/keywords, or combined filters. No ML label mapping or training-data writes are performed.
- Generated `dataset/constitution/processed/legal_reference.csv` and `inspection_report.json`: 1,070 input and processed records; 0 invalid; 0 duplicate; 0 skipped; 1 incomplete row (row index 1068) with blank `source_url` and `source_name`. Counts by code: IPC 575, Constitution of India 493, CrPC 1, BNS 1.
- Added a Legal Knowledge Base navigation page to `src/streamlit_ui.py` without removing existing pages. It distinguishes dataset descriptions from statutory text, provides a source link only for HTTP(S) URLs, includes current-law/legal-advice disclaimers, and does not map IPC to BNS.
- Added 12 reference-processing/search tests and a Streamlit page test. Ran the full suite: 69 tests passed. The existing AppTest timeout was increased from 3 to 10 seconds after a reproducible DOCX test timeout; the full suite then passed.
- Updated architecture, PRD, memory, and task documentation with the separate data flow, verified record composition, limitations, and test status. The canonical ML CSV remains empty; source register remains unapproved; no model training was run.

