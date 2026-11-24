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
↓  
Document Upload Interface  
↓  
Document Text Extraction  
↓  
NLP Text Preprocessing  
↓  
TF-IDF Feature Extraction  
↓  
Machine Learning Classification Model  
↓  
Predicted Legal Category  
↓  
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

### 4.3 NLP Preprocessing Module

This module cleans and prepares extracted legal text for machine learning.

**Processing Steps:**
- Convert text into lowercase.
- Remove unnecessary special characters.
- Remove extra spaces.
- Perform tokenization.
- Remove unnecessary stopwords where appropriate.
- Normalize textual content.

**Output:** Cleaned legal document text.

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

| Document ID | Document Text | Category |
|---|---|---|
| 001 | Theft-related legal case... | Criminal Law |
| 002 | Contract dispute between parties... | Civil Law |
| 003 | Fundamental rights and constitution... | Constitutional Law |
| 004 | Land ownership dispute... | Property Law |
| 005 | Other legal matter... | Other Legal Domains |

### Dataset Requirements

- Collect legally relevant documents from appropriate sources.
- Assign predefined category labels.
- Remove duplicate or irrelevant records.
- Ensure sufficient examples for each category.
- Divide the dataset into training and testing sets.

---

## 6. Model Training Architecture

The model training pipeline follows these steps:

1. Load the labelled legal document dataset.
2. Separate document text and category labels.
3. Perform text preprocessing.
4. Split the dataset into training and testing sets.
5. Apply TF-IDF vectorization.
6. Train Logistic Regression and/or SVM classifiers.
7. Evaluate model performance.
8. Select the best-performing model.
9. Save the trained model and TF-IDF vectorizer for future predictions.

**Important:** The same fitted TF-IDF vectorizer must be reused during prediction. It must not be independently fitted on uploaded documents.

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
│
├── dataset/
│   └── legal_documents.csv
│
├── models/
│   ├── classifier.pkl
│   └── tfidf_vectorizer.pkl
│
├── uploads/
│
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py
│   ├── text_extraction.py
│   ├── feature_extraction.py
│   ├── model_training.py
│   └── prediction.py
│
├── app.py
├── test.py
├── architecture.md
├── requirements.txt
└── README.md
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