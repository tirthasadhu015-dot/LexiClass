# LexiClass AI
## System Architecture Document

**Project Title:** Legal Document Topic Classification using NLP  
**Project Name:** LexiClass AI  
**Tagline:** Smarter Legal Documents, Simplified.  
**Technology Stack:** Python, NLP, Machine Learning, Scikit-learn, Streamlit

---

## 1. Project Overview

LexiClass AI is an NLP-based machine learning application designed to automatically classify legal documents into predefined legal topic categories based on their textual content.

The system analyzes uploaded legal documents, extracts their text, performs natural language processing, and predicts the most relevant legal category.

The primary objective is to simplify legal document organization, classification, and retrieval through automated text analysis.

### Supported Legal Categories

The system will classify documents into the following categories:

1. Criminal Law
2. Civil Law
3. Constitutional Law
4. Property Law
5. Other Legal Domains

---

## 2. System Architecture

The application follows a modular architecture consisting of six major components.

### Architecture Workflow

User  
â†“  
Document Upload Interface  
â†“  
Document Text Extraction  
â†“  
NLP Text Preprocessing  
â†“  
TF-IDF Feature Extraction  
â†“  
Machine Learning Classification Model  
â†“  
Predicted Legal Category  
â†“  
Result Display Interface

---

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Dataset management |
| NumPy | Numerical operations |
| NLTK | Natural Language Processing |
| Scikit-learn | Machine Learning |
| TF-IDF | Text feature extraction |
| Logistic Regression | Classification model |
| SVM | Alternative classification model |
| PyPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| Streamlit | Web application interface |
| Matplotlib | Data visualization |
| Seaborn | Confusion matrix visualization |

---

## 4. Core System Modules

### 4.1 Document Upload Module

This module allows users to upload legal documents through the web interface.

**Responsibilities:**
- Accept PDF and DOCX files.
- Validate file formats.
- Check whether the uploaded document contains readable text.
- Pass valid documents to the text extraction module.

### 4.2 Text Extraction Module

This module extracts textual content from uploaded documents.

**Responsibilities:**
- Read PDF documents using PyPDF.
- Extract text from DOCX files using python-docx.
- Handle empty or unreadable documents.
- Pass extracted text to the preprocessing module.


The extraction module accepts uploaded bytes and a filename, validates the `.pdf` or `.docx` extension, enforces a 20 MiB upload limit, and parses in memory without writing uploads to disk. It normalizes horizontal whitespace while preserving paragraph/page breaks. Scanned PDFs with no text layer are reported as having no extractable text; OCR is outside the initial scope.

### 4.3 NLP Preprocessing Module

This module conservatively normalizes extracted text for machine learning while preserving legal wording.

**Processing Steps:**
- Normalize Unicode composition, line endings, non-breaking spaces, and invisible formatting artifacts.
- Collapse excess horizontal whitespace and repeated blank lines while preserving paragraph boundaries.
- Preserve capitalization, punctuation, legal citations, section numbers, negations, and hyphenated terminology.
- Provide a reusable legal-aware tokenizer; do not remove stopwords by default.
- Allow optional caller-supplied stopword filtering while protecting legal negations and selected legal terms.
- Do not stem or lemmatize by default; legal terminology may change meaning under these transformations.

**Output:** Normalized text from `preprocess_text`, shared by training and inference.
### 4.4 Feature Extraction Module

This module converts processed text into numerical features using TF-IDF (Term Frequency-Inverse Document Frequency).

**Responsibilities:**
- Convert textual documents into numerical vectors.
- Identify important words and terms.
- Reduce the influence of frequently occurring common words.
- Generate feature representations for classification.

### 4.5 Machine Learning Classification Module

This is the core component of LexiClass AI.

The system uses supervised machine learning algorithms trained on labelled legal document datasets.

**Candidate Algorithms:**
- Logistic Regression
- Support Vector Machine (SVM)

**Responsibilities:**
- Load the trained classification model.
- Process the extracted document features.
- Predict the appropriate legal category.
- Return the predicted category to the application.

The final model will be selected based on evaluation results.

### 4.6 Result Display Module

This module displays the classification results to the user.

**Displayed Information:**
- Uploaded document name.
- Predicted legal category.
- Classification confidence score, if supported by the selected model.
- Document processing status.

---

## 5. Dataset Architecture

The system requires a labelled dataset containing legal documents and their corresponding categories.

### Dataset Structure

The header-only CSV schema is `document_id,document_title,text,category,source,source_url,license,language`. Add only genuine, permitted records; the template contains no example document.

### Dataset Requirements

- Collect legally relevant documents from appropriate sources.
- Assign predefined category labels.
- Remove duplicate or irrelevant records.
- Ensure sufficient examples for each category.
- Divide the dataset into training and testing sets.

The initial CSV is `dataset/legal_documents.csv`, with one reviewed row per original document. `dataset/source_register.csv` records collection-level source and license provenance. `src/dataset_validation.py` checks required schema and values, category labels, duplicate IDs and normalized text, missing direct URLs, short text requiring review, and class counts. `source_url` may be blank only when attribution is otherwise traceable in the source register; license is required. An empty template is not training data. See `dataset/README.md` for manual labeling and source-use rules.
---

## 6. Model Training Architecture

The training entry point is `train_model.py`; reusable training logic lives in `src/model_training.py` and TF-IDF setup lives in `src/feature_extraction.py`.

1. Validate the CSV schema and records with `src/dataset_validation.py`.
2. Require examples from all five categories and at least 10 records in each category. This minimum supports a stratified 80/20 holdout plus five-fold cross-validation; it is a training precondition, not a claim of statistical sufficiency for production use.
3. Normalize text with the same `preprocess_text` function used by the vectorizer during inference.
4. Create a reproducible stratified train/test split.
5. Compare Logistic Regression and Linear SVM using five-fold cross-validation on the training split. Each fold fits its own TF-IDF vectorizer only on that fold's training portion.
6. Select by mean cross-validated macro F1, with cross-validated accuracy as a tie-breaker.
7. Fit a final TF-IDF vectorizer only on the full training split; transform the held-out test split without refitting.
8. Fit both candidate classifiers on the transformed training data and report accuracy, macro precision, macro recall, macro F1, per-category metrics, and a confusion matrix on held-out data.
9. Save the selected classifier, its fitted vectorizer, and actual evaluation report under `models/`.

The vectorizer and classifier are saved separately as `tfidf_vectorizer.joblib` and `classifier.joblib`. Inference must load and reuse this exact fitted vectorizer. No artifacts are written when dataset validation or sufficiency checks fail.

**Important:** The held-out test split is not used to select the model. No metrics are available until real, valid data is supplied and training completes.
---

## 7. Model Evaluation

`evaluate_model.py` invokes `src/evaluation.py`. It requires the unchanged CSV used for training, the matching scikit-learn version, saved training metadata, both candidate classifiers, and the shared fitted vectorizer. It recreates the stratified held-out split from the recorded seed and verifies the dataset SHA-256 before scoring. Training data is never substituted for test data.

For each candidate, evaluation generates accuracy, macro precision, macro recall, macro F1, per-category precision/recall/F1/support, a classification report, and a confusion matrix. It also reports training/test class distributions and flags a possible training class imbalance when the largest-to-smallest class ratio is at least 1.5; this is a screening heuristic, not a guarantee of bias or quality.

Successful runs save `reports/evaluation/evaluation_report.json`, `classification_report.txt`, `model_comparison.csv`, two confusion-matrix figures, a metric comparison figure, and a training class-distribution figure. If data, model artifacts, or matching provenance are unavailable, evaluation stops without generating reports or figures. Performance remains informational and depends on dataset size, label quality, class balance, source diversity, and the single held-out split.
---

## 8. Project Folder Structure

```text
LexiClass_AI/
â”‚
â”œâ”€â”€ dataset/
â”‚   â””â”€â”€ legal_documents.csv
â”‚
â”œâ”€â”€ models/
â”‚   â”œâ”€â”€ classifier.pkl
â”‚   â””â”€â”€ tfidf_vectorizer.pkl
â”‚
â”œâ”€â”€ uploads/
â”‚
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ data_preprocessing.py
â”‚   â”œâ”€â”€ text_extraction.py
â”‚   â”œâ”€â”€ feature_extraction.py
â”‚   â”œâ”€â”€ model_training.py
â”‚   â””â”€â”€ prediction.py
â”‚
â”œâ”€â”€ app.py
â”œâ”€â”€ test.py
â”œâ”€â”€ architecture.md
â”œâ”€â”€ requirements.txt
â””â”€â”€ README.md
```

---

## Streamlit Interface Layer

`app.py` is the Streamlit entry point and delegates presentation to `src/streamlit_ui.py`. The UI calls the existing document extraction and prediction modules; it does not implement parsing or model logic itself. Inference normalizes extracted text with `preprocess_text`, transforms it using the saved fitted TF-IDF vectorizer, and passes those features to the saved classifier. Navigation includes only the implemented Dashboard, Classify Document, and About pages. Uploaded bytes remain in memory, with the 20 MiB limit enforced by Streamlit configuration and the extraction module. Classification stays unavailable unless both the trained classifier and its fitted vectorizer are present.
## 9. Application Workflow

The complete application will work as follows:

**Step 1:** The user opens the LexiClass AI web application.

**Step 2:** The user uploads a legal document in PDF or DOCX format.

**Step 3:** The system validates the uploaded document.

**Step 4:** Text is extracted from the document.

**Step 5:** The extracted text is cleaned using NLP preprocessing techniques.

**Step 6:** TF-IDF converts the processed text into numerical features.

**Step 7:** The trained machine learning model analyzes the features and predicts the legal category.

**Step 8:** The predicted category is displayed on the application interface.

---

## 10. Error Handling and Limitations

The system should handle the following situations:

- Unsupported document formats.
- Empty or unreadable documents.
- Documents containing scanned images without extractable text.
- Missing or corrupted model files.
- Insufficient document content.
- Uncertain or potentially incorrect predictions.

### Limitations

- Classification accuracy depends on dataset quality and diversity.
- The system may not correctly classify documents outside its trained categories.
- Scanned documents require OCR support, which is not included in the initial version.
- The prediction is an automated classification result, not legal advice.
- Model predictions should be reviewed by qualified legal professionals before being used for important decisions.

---

## 11. Future Enhancements

Potential future improvements include:

- OCR support for scanned legal documents.
- Multilingual legal document classification.
- Advanced transformer-based NLP models.
- Automatic legal document summarization.
- Search and filtering of previously uploaded documents.
- Document classification history.
- Improved explainability of model predictions.

---

## 12. Conclusion

LexiClass AI aims to provide an automated and efficient solution for legal document topic classification using Natural Language Processing and Machine Learning.

By combining document text extraction, NLP preprocessing, TF-IDF feature extraction, and supervised classification algorithms, the system will help users organize legal documents into predefined topic categories.

The modular architecture ensures that the application remains maintainable, scalable, and suitable for future enhancements.

## Separate Legal Knowledge Base

`src/legal_knowledge_base.py` provides an independent reference-data path. It loads the UTF-8 JSON source at `dataset/raw/indian_constitution.json`, validates the root list and record shape, preserves the ten source fields and source-provided URL, reports invalid/duplicate/incomplete records, and generates `dataset/constitution/processed/legal_reference.csv` plus `inspection_report.json`. Incomplete dictionary records are retained with empty source fields and counted; malformed non-dictionary rows and exact duplicates are reported and skipped. Reprocessing replaces only these generated outputs with a same-directory atomic replacement per file and never writes the source JSON.

Search uses case-insensitive exact Act-code and section filters plus substring matching across title, description, keywords, purpose, and context. Combined filters are conjunctive. This knowledge base is separate from `dataset/legal_documents.csv`, annotation labels, TF-IDF training, and classifier inference. It does not map Acts or sections to the five ML categories.

`src/streamlit_ui.py` adds a Legal Knowledge Base page while retaining Dashboard, Classify Document, and About Project. Results identify descriptions as dataset-provided, include purpose/context/penalty fields, and link to a source URL only when it is HTTP(S). Users are told to verify exact wording and current legal status at the provided source. The interface does not claim dataset summaries are official statutory wording, assert provisions are in force, or translate IPC entries into BNS entries. Results are reference aids only, not legal advice.
