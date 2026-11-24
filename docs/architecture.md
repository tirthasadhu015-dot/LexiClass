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

| document_id | text | category | source | source_url | license |
|---|---|---|---|---|---|
| *(empty template; add only genuine, permitted records)* | | | | | |

### Dataset Requirements

- Collect legally relevant documents from appropriate sources.
- Assign predefined category labels.
- Remove duplicate or irrelevant records.
- Ensure sufficient examples for each category.
- Divide the dataset into training and testing sets.

The initial CSV is `dataset/legal_documents.csv`. `src/dataset_validation.py` checks required columns, missing identifiers/text/labels/source, supported category labels, duplicate identifiers, duplicate normalized text, and reports counts for every supported category. `source` should provide a traceable citation or collection name; `source_url` and `license` provide additional provenance details when available. An empty template is not training data.
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

The classification model will be evaluated using the following performance metrics:

- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix

These metrics will help determine how accurately the system classifies legal documents across different categories.

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





