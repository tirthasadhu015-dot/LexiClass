# LexiClass AI â€” Development Tasks

**Project Name:** LexiClass AI  
**Tagline:** Smarter Legal Documents, Simplified.  
**Project Type:** Legal Document Topic Classification using NLP and Machine Learning

---

## 1. Project Setup

- [ ] Create the project folder.
- [ ] Open the project in VS Code.
- [ ] Create a Python virtual environment.
- [ ] Activate the virtual environment.
- [ ] Install all required Python libraries.
- [x] Create the initial project folder structure.
- [x] Create `requirements.txt`.
- [ ] Test all library imports.
- [ ] Initialize Git repository (optional).

## 2. Dataset Collection and Preparation

- [ ] Research suitable legal document datasets.
- [ ] Collect legal documents from permitted sources.
- [ ] Ensure documents are suitable for academic use.
- [ ] Identify relevant text and document content.
- [ ] Assign labels to the collected documents.
- [ ] Organize documents into the required categories:
  - [ ] Criminal Law
  - [ ] Civil Law
  - [ ] Constitutional Law
  - [ ] Property Law
  - [ ] Other Legal Domains
- [ ] Remove duplicate documents.
- [ ] Check missing or incorrect labels.
- [ ] Save the prepared dataset in CSV format.
- [ ] Review the dataset for class imbalance.

## 3. Document Text Extraction

- [ ] Install and configure PyPDF.
- [ ] Install and configure python-docx.
- [ ] Create a document extraction module.
- [ ] Implement PDF text extraction.
- [ ] Implement DOCX text extraction.
- [ ] Add file format validation.
- [ ] Handle empty or unreadable documents.
- [ ] Test extraction using sample PDF files.
- [ ] Test extraction using sample DOCX files.

## 4. Text Preprocessing

- [ ] Create a text preprocessing module.
- [ ] Convert text into a consistent format.
- [ ] Remove unnecessary whitespace.
- [ ] Remove irrelevant special characters where appropriate.
- [ ] Tokenize the extracted text.
- [ ] Apply stop-word handling carefully.
- [ ] Apply stemming or lemmatization if appropriate.
- [ ] Preserve important legal terms and negations.
- [ ] Test the preprocessing pipeline.

## 5. Feature Extraction

- [ ] Import TF-IDF Vectorizer from Scikit-learn.
- [ ] Configure suitable TF-IDF parameters.
- [ ] Convert training text into numerical features.
- [ ] Save the fitted TF-IDF vectorizer.
- [ ] Ensure the same vectorizer is reused during prediction.
- [ ] Check feature dimensions and output.

## 6. Machine Learning Model Development

- [ ] Prepare input features and target labels.
- [ ] Split the dataset into training and testing sets.
- [ ] Use stratified splitting when appropriate.
- [ ] Train a Logistic Regression model.
- [ ] Train an SVM model.
- [ ] Compare model performance.
- [ ] Select the most suitable model.
- [ ] Save the trained model.
- [ ] Save the fitted vectorizer.
- [ ] Test predictions using unseen documents.

## 7. Model Evaluation

- [ ] Calculate accuracy.
- [ ] Calculate precision.
- [ ] Calculate recall.
- [ ] Calculate F1-score.
- [ ] Generate a confusion matrix.
- [ ] Review performance for each category.
- [ ] Identify possible classification errors.
- [ ] Check for data leakage.
- [ ] Document actual evaluation results.

## 8. Streamlit Web Application

- [ ] Create `app.py`.
- [ ] Configure the Streamlit page.
- [ ] Create the application header.
- [ ] Add the LexiClass AI branding.
- [ ] Design the sidebar navigation.
- [ ] Create the document upload section.
- [ ] Support PDF uploads.
- [ ] Support DOCX uploads.
- [ ] Display extracted text where appropriate.
- [ ] Add a classification button.
- [ ] Connect the trained model to the application.
- [ ] Display the predicted legal category.
- [ ] Display prediction confidence carefully.
- [ ] Add an error message for unsupported files.
- [ ] Create an About section.

## 9. Testing and Debugging

- [ ] Test PDF document uploads.
- [ ] Test DOCX document uploads.
- [ ] Test empty documents.
- [ ] Test unsupported file formats.
- [ ] Test documents from all five categories.
- [ ] Check model prediction consistency.
- [ ] Check application navigation.
- [ ] Fix identified bugs.
- [ ] Test the complete application workflow.

## 10. Documentation

- [ ] Complete `README.md`.
- [ ] Maintain `architecture.md`.
- [ ] Maintain `design.md`.
- [ ] Maintain `prd.md`.
- [ ] Maintain `rules.md`.
- [ ] Maintain `memory.md`.
- [ ] Maintain this `tasks.md`.
- [ ] Add installation instructions.
- [ ] Add project screenshots.
- [ ] Document dataset sources.
- [ ] Document model evaluation results.
- [ ] Mention project limitations.

## 11. Final Project Preparation

- [ ] Verify the final folder structure.
- [ ] Check `requirements.txt`.
- [ ] Remove unnecessary files.
- [ ] Run the application from a clean environment.
- [ ] Prepare a project demonstration.
- [ ] Prepare presentation slides.
- [ ] Prepare a project report.
- [ ] Review the project before submission.

---

## Development Guidelines

1. Complete tasks phase by phase.
2. Test each module before moving to the next phase.
3. Keep dataset processing, model training, and UI code separate.
4. Never use fake model accuracy or fabricated evaluation results.
5. Avoid training and testing data leakage.
6. Validate uploaded files before processing.
7. Do not present predictions as professional legal advice.
8. Update this task list whenever project requirements change.

---

## Current Progress

**Status:** The ML training CSV remains empty and no classifier has been trained. A separate legal-reference knowledge base is implemented from the existing JSON: 1,070 rows processed, with one incomplete source record, no invalid records, and no duplicates. The full test suite passes (69 tests). No source-register approval was made.

**Next Priority:** Verify legal reference details and source links as needed. Separately, review source rights for ML training, add genuine categorized documents, adjudicate labels, and validate; the training design requires at least 10 usable documents per category before training.

**Completion Rule:** Mark a task as completed only after it has been implemented and tested.
