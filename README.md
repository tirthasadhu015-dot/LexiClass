# LexiClass AI

**Smarter Legal Documents, Simplified.**

LexiClass AI is a Python and Streamlit project for classifying legal PDF and DOCX documents into Criminal Law, Civil Law, Constitutional Law, Property Law, or Other Legal Domains. The PDF/DOCX text extraction module is implemented; classification and model training are not implemented. No trained model is included.

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

The initial Streamlit page only confirms that setup is in progress. Classification requires a permitted, labeled dataset and a trained model, neither of which is included.

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
| `text` | Genuine legal document text that is permitted for this use |
| `category` | One of the five supported category labels |
| `source` | Citation, collection name, or other traceable source description |
| `source_url` | Optional URL for locating the source |
| `license` | Optional license or documented usage terms |

Keep the original citation and usage terms traceable. Do not include confidential material or documents without permission. Add actual sourced records only; do not treat this empty template as training data.

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
