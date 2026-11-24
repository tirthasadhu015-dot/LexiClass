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

