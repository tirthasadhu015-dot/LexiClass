# LexiClass AI — Project Memory

## 1. Project Identity

- **Project Name:** LexiClass AI
- **Project Title:** Legal Document Topic Classification using NLP
- **Tagline:** Smarter Legal Documents, Simplified.
- **Project Type:** Machine Learning and Natural Language Processing Application
- **Primary Language:** Python
- **Frontend Framework:** Streamlit

LexiClass AI is an AI-powered application designed to classify legal documents into predefined legal categories using Natural Language Processing and Machine Learning techniques.

---

## 2. Project Objective

The objective of LexiClass AI is to automatically analyze legal document text and identify the most relevant legal topic category.

The application should allow users to upload supported legal documents, extract textual content, process the text using NLP techniques, and predict the document's legal category using a trained machine learning model.

The project is intended for educational, research, and document organization purposes.

---

## 3. Legal Categories

The initial classification system will support the following categories:

1. Criminal Law
2. Civil Law
3. Constitutional Law
4. Property Law
5. Other Legal Domains

These categories should remain consistent across the dataset, model training, prediction logic, and UI.

---

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Dataset management |
| NumPy | Numerical operations |
| NLTK | Text preprocessing |
| Scikit-learn | Machine learning |
| TF-IDF | Text feature extraction |
| Logistic Regression | Classification |
| Support Vector Machine | Alternative classification |
| PyPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| Streamlit | Web application |
| Matplotlib | Visualization |
| Seaborn | Evaluation visualizations |

---

## 5. Project Architecture

The application follows a modular pipeline:

User  
→ Document Upload  
→ File Validation  
→ Text Extraction  
→ NLP Preprocessing  
→ TF-IDF Feature Extraction  
→ Machine Learning Classification  
→ Result Display

Each module should have a clearly defined responsibility.

---

## 6. Project Folder Structure

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
├── design.md
├── memory.md
├── requirements.txt
└── README.md
```

---

## 7. Dataset Guidelines

The dataset should contain legal document text and corresponding category labels.

### Dataset Columns

- Document ID
- Document Text
- Category

### Dataset Requirements

- Use relevant legal documents.
- Maintain consistent category labels.
- Remove duplicate and irrelevant records.
- Ensure reasonable representation of all categories.
- Use appropriate training and testing splits.
- Avoid data leakage between training and testing.

Dataset file:

`dataset/legal_documents.csv`

---

## 8. NLP Processing Guidelines

The preprocessing pipeline may include:

1. Text extraction.
2. Lowercase conversion.
3. Removal of unnecessary special characters.
4. Whitespace normalization.
5. Tokenization.
6. Stopword removal where appropriate.
7. Text normalization.

Preprocessing should be consistent between training and prediction.

Do not unnecessarily remove important legal terminology, section references, numbers, or negation words that may influence classification.

---

## 9. Machine Learning Guidelines

The initial model pipeline should use:

- TF-IDF feature extraction.
- Logistic Regression.
- Support Vector Machine as an alternative model.

### Training Workflow

1. Load the labelled dataset.
2. Validate the dataset.
3. Separate text and labels.
4. Split the dataset into training and testing subsets.
5. Fit the TF-IDF vectorizer on training data only.
6. Transform training and testing data.
7. Train the classification model.
8. Evaluate performance.
9. Select the best-performing model.
10. Save the trained model and vectorizer.

### Important Rules

- Never fit the TF-IDF vectorizer independently on uploaded documents.
- Reuse the same fitted vectorizer during prediction.
- Prevent data leakage.
- Use reproducible train-test splitting.
- Do not claim model accuracy without actual evaluation.
- Select the final model based on measured results.

---

## 10. Model Evaluation

The system should evaluate the trained model using:

- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix

Evaluation results should be based on the actual test dataset.

Performance metrics must not be fabricated.

---

## 11. Application Features

### Document Classification

- Upload PDF and DOCX files.
- Validate file type and size.
- Extract document text.
- Preprocess extracted content.
- Predict legal category.
- Display classification results.

### Dashboard

- Application overview.
- Classification workflow.
- Statistics based on real data.
- Quick access to document classification.

### Classification Result

Display:

- Uploaded document name.
- Predicted legal category.
- Confidence score, if supported by the model.
- Processing status.
- Option to classify another document.

### Classification History

History functionality may be implemented later.

If implemented, it should store and display actual classification records rather than fabricated data.

---

## 12. UI/UX Design Guidelines

Follow `design.md` as the primary design reference.

### Brand Colors

- Deep Navy: `#0F172A`
- Royal Blue: `#2563EB`
- Light Blue: `#DBEAFE`
- White: `#FFFFFF`
- Slate Gray: `#64748B`
- Light Gray: `#F1F5F9`
- Success Green: `#16A34A`
- Warning Amber: `#F59E0B`
- Error Red: `#DC2626`

### Design Style

- Modern
- Minimal
- Professional
- Trustworthy
- Responsive
- Clean dashboard-based interface

### UI Rules

- Maintain consistent spacing.
- Use reusable components.
- Keep the interface uncluttered.
- Use clear typography.
- Display appropriate loading and error states.
- Maintain accessibility and readability.

---

## 13. Development Rules

- Use Python and Streamlit.
- Maintain modular code.
- Separate frontend logic from ML logic.
- Keep reusable functions inside appropriate modules.
- Use descriptive variable and function names.
- Avoid unnecessary code duplication.
- Validate user inputs and uploaded files.
- Handle exceptions gracefully.
- Keep code readable and beginner-friendly.
- Explain important code changes during development.
- Do not unnecessarily modify unrelated modules.
- Preserve the existing folder structure unless a change is required.

---

## 14. Security and Privacy

- Validate uploaded files before processing.
- Restrict supported file types.
- Avoid executing uploaded document contents.
- Do not expose sensitive file paths.
- Avoid storing uploaded documents unnecessarily.
- Handle uploaded files securely.
- Do not use confidential legal documents without appropriate permission.

---

## 15. Limitations

- Model predictions depend on dataset quality.
- The model may perform poorly on unseen legal domains.
- Scanned PDFs may require OCR.
- Classification confidence does not guarantee correctness.
- The application is not a substitute for legal advice.
- Important legal decisions should not rely solely on automated classification.

---

## 16. Future Enhancements

Possible future features:

- OCR support.
- Multilingual legal document classification.
- Transformer-based NLP models.
- Legal document summarization.
- Advanced search and filtering.
- Classification history.
- Model explainability.
- Additional legal categories.
- Improved dataset quality and model accuracy.

---

## 17. AI Coding Assistant Instructions

When working on LexiClass AI:

1. Read `memory.md` to understand the overall project context.
2. Read `architecture.md` before implementing system logic.
3. Read `design.md` before modifying the UI.
4. Maintain consistency with the defined architecture and design system.
5. Do not invent dataset statistics, model performance, or classification results.
6. Implement features incrementally.
7. Explain important code changes in beginner-friendly language.
8. Ensure the application runs correctly before claiming a feature is complete.
9. Prefer reliable, maintainable, and simple solutions.
10. Treat legal classification predictions as informational outputs, not legal advice.

---

## 18. Project Development Priority

Follow this development sequence:

1. Environment Setup
2. Dataset Collection and Preparation
3. Text Extraction
4. NLP Preprocessing
5. Feature Extraction
6. Model Training
7. Model Evaluation
8. Prediction Pipeline
9. Streamlit Application
10. Testing
11. Documentation
12. Final Presentation

---

## 19. Project Success Criteria

LexiClass AI will be considered functionally complete when:

- A labelled dataset is prepared.
- Document text can be extracted.
- NLP preprocessing is implemented.
- A classification model is trained.
- The model is evaluated using appropriate metrics.
- The trained model can classify new supported documents.
- The Streamlit application works correctly.
- The application displays prediction results.
- Errors are handled appropriately.
- Project documentation is completed.

---

**Project Identity:** LexiClass AI  
**Core Principle:** Intelligent Legal Classification with a Simple and Reliable User Experience.