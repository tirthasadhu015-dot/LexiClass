# LexiClass AI

**Smarter Legal Documents, Simplified.**

LexiClass AI is a Python and Streamlit project for classifying legal PDF and DOCX documents into Criminal Law, Civil Law, Constitutional Law, Property Law, or Other Legal Domains. The document extraction, preprocessing, training/evaluation pipeline, and Streamlit interface are implemented. The dataset currently has no labeled records, so no trained model is included and classification is unavailable.

## Requirements

- Python 3.10 or newer
- Windows and PowerShell (the commands below also work in the VS Code terminal)

## Setup

From the project directory, create and activate a virtual environment, then install the project dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

The Streamlit interface includes a dashboard, document classification page, and project information page. Classification remains unavailable until a permitted, labeled dataset is used to train a model.

## Project layout

- `app.py` — Streamlit entry point
- `src/` — extraction, preprocessing, feature, training, and prediction modules
- `dataset/` — reserved for the sourced and labeled dataset
- `models/` — reserved for trained model artifacts
- `uploads/` — reserved for temporary uploads if later required
- `docs/` — project requirements and development guidance

See `docs/` for the architecture, requirements, design system, and development rules. Predictions are intended for informational document organization only, not legal advice.

## Dataset format and validation

`dataset/legal_documents.csv` is an empty template; it contains no legal documents or dataset statistics. Its columns are:

| Column | Purpose |
|---|---|
| `document_id` | Stable unique identifier for the record |
| `document_title` | Title shown by the source |
| `text` | Genuine legal document text that is permitted for this use |
| `category` | One of the five supported category labels |
| `source` | Source ID from the source register or traceable citation |
| `source_url` | Direct document URL, when available |
| `license` | Exact applicable license or documented use terms |
| `language` | Document language, preferably an ISO 639-1 code |

`dataset/source_register.csv` records dataset-level source, version, format, license, terms, attribution, and review status. Keep citations and usage terms traceable. Do not include confidential material or documents without permission. Add actual sourced records only; do not treat this empty template as training data. See [dataset/README.md](dataset/README.md) for collection steps, manual labeling rules, duplicate handling, validation details, and the reviewed candidate-source assessment.

Validate the CSV and print its row count and distribution across all five categories:

```powershell
python -m src.dataset_validation
```

To validate a different CSV, pass its path:

```powershell
python -m src.dataset_validation path\to\legal_documents.csv
```

## Document text extraction

The extraction module accepts the uploaded filename and file bytes, returns normalized text, and does not save uploads. PDF and DOCX uploads are limited to 20 MiB; unsupported extensions, empty files, corrupt packages, and documents with no extractable text produce clear errors. Whitespace normalization keeps paragraph and page boundaries. Scanned PDFs need OCR and are not supported in this version.

Run the extraction tests from the project root with:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```


## NLP text preprocessing

`src/data_preprocessing.py` provides reusable normalization, tokenization, optional stopword filtering, and a `preprocess_text` entry point for both future training and inference code. By default it preserves legal wording, case, punctuation, section references, negations, and paragraph boundaries while cleaning whitespace and invisible formatting artifacts. Stopword filtering is off by default; if explicitly enabled, caller-selected stop words are used and protected negations/legal terms remain. Stemming and lemmatization are omitted to avoid changing legal terms.

Run all project unit tests from the project root with:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Model training

After adding genuine labeled data to `dataset/legal_documents.csv`, run:

```powershell
python train_model.py
```

Training requires all five categories and at least 10 valid records per category. The script reports missing or insufficient labels and exits without model artifacts when the data cannot support the planned stratified holdout and five-fold cross-validation. The 10-per-category threshold is a technical minimum for this evaluation design, not a guarantee of model quality.

The script compares Logistic Regression and Linear SVM using mean five-fold cross-validated macro F1 on the training split, then reports each model's actual metrics on a stratified held-out test split. The test split is not used for selection. On successful training, it writes `classifier.joblib`, `tfidf_vectorizer.joblib`, and `evaluation_report.json` to `models/`. Inference must reuse the saved vectorizer through `src/prediction.py`.

Run the unit tests with:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Model evaluation

Run evaluation only after training succeeds and the original CSV remains unchanged:

```powershell
python evaluate_model.py
```

The evaluator verifies dataset provenance and recreates the recorded stratified test split. It compares the saved Logistic Regression and Linear SVM candidates using only that held-out data. Reports and figures are written to `reports/evaluation/`. With the current header-only dataset (0 records), evaluation correctly stops and produces no scores or figures.

## Streamlit interface

Start the app from the project root:

```powershell
streamlit run app.py
```

The interface supports PDF and DOCX uploads up to 20 MiB. Uploaded documents are processed in memory, and the app shows extracted text before classification. The classify action remains disabled until both trained model artifacts are present. No accuracy, prediction, or confidence is shown without real model output.

## Final project status

### Overview and architecture

LexiClass AI is a legal document organization project for five broad categories: Criminal Law, Civil Law, Constitutional Law, Property Law, and Other Legal Domains. The workflow is:

`Streamlit upload -> PDF/DOCX validation and extraction -> legal text preprocessing -> saved fitted TF-IDF vectorizer -> saved classifier -> category display`

Presentation lives in `src/streamlit_ui.py`; extraction, preprocessing, vectorization, training, evaluation, and prediction are separate modules under `src/`. Uploads remain in memory. The app is informational and does not provide legal advice.

### Technology stack

Python, Streamlit, pandas, NumPy, scikit-learn (TF-IDF, Logistic Regression, Linear SVM), joblib (model serialization), NLTK (declared dependency; not currently used by the active preprocessing pipeline), PyPDF, python-docx, Matplotlib, and Seaborn.

### Implemented features

- CSV schema validation, duplicate and category checks, and class distribution reporting.
- In-memory PDF and DOCX extraction, including empty/corrupt file handling and a 20 MiB upload cap.
- Conservative legal text normalization that preserves legal wording and negations.
- Shared TF-IDF training/inference configuration, model training and held-out evaluation scripts, and guarded artifact loading.
- Streamlit dashboard, upload/text preview, classification page, and About page. Classification stays disabled until a classifier and fitted vectorizer are available.
- Unit and Streamlit upload integration tests.

### Dataset, sources, and licensing

`dataset/legal_documents.csv` contains only its header (0 records). No document sources or dataset licenses have been added, so there is no source provenance to report yet. The CSV has `source`, `source_url`, and `license` fields to record citations and permitted-use terms for future genuine records. Do not add confidential or unlicensed documents.

### Model evaluation results

No trained classifier or vectorizer exists in `models/`, and no evaluation report or figures exist. The dataset validator reports 0 records in each category. Running `evaluate_model.py` stops with “The dataset contains 0 labeled records”; therefore no accuracy, precision, recall, F1, confusion matrix, or classification report is available. No model performance is claimed.

### Screenshots

No application screenshots are included in the repository.

### Known limitations and future improvements

- Genuine classification requires permitted labeled data, successful training, and evaluation. This is the main pending requirement.
- Scanned PDFs are unsupported because OCR is not implemented.
- Dataset diversity, source licensing, label quality, and class balance remain unassessed until data is added.
- Future work: collect and document lawful data sources, train and evaluate with genuine records, validate actual saved-model predictions, then consider OCR, classification history, and broader evaluation on external data.

### Final task status

| Status | Tasks |
|---|---|
| Completed and verified | Modular extraction and preprocessing; dataset validation; training/evaluation pipeline implementation; Streamlit upload integration; 34 automated tests passing. |
| Partially completed | Prediction flow and artifact loading are implemented and covered with contract/error tests, but no trained artifacts are available for a genuine classification test. |
| Pending | Add licensed, traceable labeled data; train and evaluate actual models; verify real predictions and record measured performance. |
