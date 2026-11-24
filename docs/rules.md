# LexiClass AI — Development Rules

## 1. General Project Rules

1. Always follow the project requirements defined in `prd.md`.
2. Follow `architecture.md` for system architecture and module responsibilities.
3. Follow `design.md` for UI/UX implementation.
4. Follow `memory.md` for project context and development decisions.
5. Maintain consistency across all project modules.
6. Do not introduce unnecessary features without approval.
7. Do not change the core project objective.
8. Keep the application simple, professional, and maintainable.

## 2. Technology Rules

The project must primarily use:

- Python
- Pandas
- NumPy
- NLTK
- Scikit-learn
- Streamlit
- PyPDF
- python-docx
- Matplotlib
- Seaborn

Rules:

1. Use Python as the primary programming language.
2. Use Streamlit for the web application.
3. Use Scikit-learn for machine learning.
4. Use TF-IDF for initial text feature extraction.
5. Use Logistic Regression and SVM as candidate classification algorithms.
6. Avoid unnecessary frameworks and dependencies.
7. Do not introduce additional technologies without a valid reason.

## 3. Code Quality Rules

1. Write clean, readable, and maintainable Python code.
2. Use meaningful variable and function names.
3. Follow Python naming conventions.
4. Use functions for reusable operations.
5. Avoid unnecessary code duplication.
6. Keep functions focused on a single responsibility.
7. Add comments where logic needs clarification.
8. Use appropriate exception handling.
9. Avoid hardcoded file paths.
10. Use `pathlib` for reliable file path management where appropriate.
11. Do not leave incomplete functions or unnecessary placeholder code.
12. Remove unused imports and variables.

## 4. Project Structure Rules

Maintain the existing folder structure:

```text
LexiClass_AI/
│
├── dataset/
├── models/
├── uploads/
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
├── prd.md
├── rules.md
├── requirements.txt
└── README.md
```

Rules:

1. Keep source code inside the appropriate modules.
2. Do not place all application logic inside `app.py`.
3. Store datasets inside `dataset/`.
4. Store trained models inside `models/`.
5. Store temporary uploaded files inside `uploads/` when necessary.
6. Do not create unnecessary files or folders.
7. Update documentation when significant architectural changes are made.

## 5. Dataset Rules

1. Use legally relevant and appropriately sourced documents.
2. Maintain consistent category labels.
3. Remove duplicate records.
4. Handle missing and invalid records.
5. Avoid fabricated dataset statistics.
6. Maintain reasonable representation across categories.
7. Keep training and testing data separate.
8. Prevent data leakage.
9. Document dataset sources and applicable usage restrictions.
10. Never use confidential legal documents without authorization.

Initial categories:

- Criminal Law
- Civil Law
- Constitutional Law
- Property Law
- Other Legal Domains

## 6. NLP Processing Rules

1. Extract text before preprocessing.
2. Normalize text consistently.
3. Remove unnecessary special characters.
4. Handle extra whitespace.
5. Apply tokenization where appropriate.
6. Apply stopword removal carefully.
7. Preserve meaningful legal terminology.
8. Do not remove important legal references, section numbers, or negation words without justification.
9. Use the same preprocessing pipeline during training and prediction.
10. Handle empty or insufficient text appropriately.

## 7. Machine Learning Rules

1. Use supervised machine learning for initial classification.
2. Use TF-IDF for text vectorization.
3. Evaluate Logistic Regression and SVM.
4. Use reproducible training and testing splits.
5. Fit the vectorizer only on training data.
6. Reuse the same fitted vectorizer during inference.
7. Save trained models using appropriate serialization.
8. Load saved models instead of retraining on every application launch.
9. Evaluate models before selecting the final classifier.
10. Do not fabricate accuracy or evaluation results.
11. Do not guarantee predictions are correct.
12. Keep model training and prediction logic separate.

## 8. Legal Classification Rules

The classifier must predict one of the predefined categories:

1. Criminal Law
2. Civil Law
3. Constitutional Law
4. Property Law
5. Other Legal Domains

Additional requirements:

- Do not invent legal categories.
- Do not claim that classification is equivalent to legal interpretation.
- Handle documents containing multiple legal topics carefully.
- Display uncertain predictions responsibly.
- Do not present the application as a legal advice system.
- Treat predictions as informational results requiring human verification.

## 9. File Upload and Security Rules

1. Accept only supported file formats.
2. Validate uploaded file extensions and content.
3. Apply reasonable upload size limits.
4. Handle corrupted documents safely.
5. Do not execute uploaded file contents.
6. Do not expose internal server paths.
7. Avoid permanently storing unnecessary uploaded documents.
8. Handle temporary files securely.
9. Do not expose sensitive information in error messages.
10. Clean up temporary files when they are no longer needed.

## 10. UI/UX Rules

Follow `design.md` strictly.

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

### Design Requirements

1. Maintain a professional legal-tech appearance.
2. Use consistent spacing and typography.
3. Prefer clean dashboard layouts.
4. Keep navigation simple.
5. Use reusable UI components.
6. Provide clear upload instructions.
7. Display loading indicators during processing.
8. Display clear success and error messages.
9. Maintain responsive layouts.
10. Avoid unnecessary animations and decorative elements.
11. Never display fake dashboard statistics.
12. Ensure text remains readable on all screen sizes.

## 11. Streamlit Rules

1. Use Streamlit for application development.
2. Keep UI code separate from business logic.
3. Use Streamlit session state only when necessary.
4. Avoid unnecessary page reloads.
5. Cache reusable resources appropriately.
6. Handle exceptions without crashing the application.
7. Provide meaningful feedback during document processing.
8. Keep the interface responsive.
9. Avoid loading the ML model repeatedly on every interaction.
10. Ensure the application can run using:

```bash
streamlit run app.py
```

## 12. Error Handling Rules

The application must handle:

- Unsupported file formats.
- Empty documents.
- Corrupted PDF files.
- Unreadable DOCX files.
- Missing dataset files.
- Missing model files.
- Insufficient document text.
- Prediction failures.
- Invalid input data.

Rules:

1. Display understandable error messages.
2. Do not expose internal stack traces to ordinary users.
3. Log useful technical errors during development.
4. Prevent application crashes wherever reasonably possible.
5. Never silently ignore important failures.

## 13. Testing Rules

1. Test each module independently.
2. Test PDF extraction.
3. Test DOCX extraction.
4. Test preprocessing functions.
5. Test feature extraction.
6. Test model loading.
7. Test prediction functionality.
8. Test invalid file uploads.
9. Test empty documents.
10. Test the complete application workflow.

Do not mark a feature as completed until it has been tested.

## 14. Documentation Rules

Maintain the following documentation:

- `architecture.md`: Technical architecture.
- `design.md`: UI/UX design system.
- `memory.md`: Project context and development decisions.
- `prd.md`: Product requirements.
- `rules.md`: Development standards.
- `README.md`: Project introduction and setup instructions.

Update documentation whenever important project decisions change.

## 15. AI Coding Assistant Rules

Any AI coding assistant working on LexiClass AI must follow these instructions:

1. Read all relevant project documentation before making significant changes.
2. Understand the existing source code before editing it.
3. Do not rewrite working code unnecessarily.
4. Do not modify unrelated files.
5. Follow the existing architecture.
6. Follow the defined design system.
7. Explain important changes clearly.
8. Provide complete code when requested.
9. Mention required dependencies.
10. Provide exact commands for running and testing changes.
11. Do not claim successful execution without verification.
12. Ask for clarification before making major architectural changes.
13. Do not introduce fake data or fake performance metrics.
14. Maintain backward compatibility where reasonably possible.

## 16. Dependency Management Rules

1. Maintain `requirements.txt`.
2. Include only required dependencies.
3. Avoid unnecessary package installations.
4. Keep dependency versions compatible.
5. Use the project's virtual environment.
6. Test the application after significant dependency changes.

## 17. Development Workflow Rules

Follow this workflow for every major feature:

1. Understand the requirement.
2. Check the existing project structure.
3. Identify the relevant module.
4. Plan the implementation.
5. Write or modify code.
6. Test the implementation.
7. Fix errors.
8. Update documentation if needed.
9. Confirm the feature works before moving forward.

## 18. Strict Restrictions

The following practices are prohibited:

- Fabricating machine learning accuracy.
- Using random predictions as actual model results.
- Displaying fake classification history.
- Hardcoding prediction outputs.
- Ignoring document validation.
- Mixing all project logic into one file.
- Removing important legal terminology without justification.
- Claiming that AI predictions are legally authoritative.
- Making major design changes without considering `design.md`.
- Replacing existing functionality without a valid reason.

## 19. Final Development Principle

Every implementation must prioritize:

- Correctness
- Reliability
- Maintainability
- Security
- Readability
- Consistent UI/UX
- Actual machine learning functionality

**Golden Rule:**

"Build real functionality first, maintain professional design, and never sacrifice correctness for appearance."

---

**Project:** LexiClass AI  
**Tagline:** Smarter Legal Documents, Simplified.