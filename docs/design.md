# LexiClass AI
## UI/UX Design System

**Project Name:** LexiClass AI  
**Tagline:** Smarter Legal Documents, Simplified.  
**Product Type:** AI-Powered Legal Document Classification Platform  
**Design Style:** Modern, Minimal, Professional, Trustworthy

---

# 1. Design Philosophy

LexiClass AI should provide a clean, professional, and user-friendly interface for classifying legal documents using Artificial Intelligence and Machine Learning.

The design should communicate:

- Trust and reliability
- Artificial Intelligence and innovation
- Legal professionalism
- Simplicity and accessibility
- Clear information hierarchy

The interface should be easy to navigate, even for users without technical or legal expertise.

Avoid unnecessary animations, excessive colors, complicated layouts, and visual clutter.

---

# 2. Brand Identity

### Brand Name
LexiClass AI

### Brand Meaning
- Lexi: Represents legal language and terminology.
- Class: Represents document classification.
- AI: Represents Artificial Intelligence.

### Tagline
"Smarter Legal Documents, Simplified."

### Brand Personality
- Intelligent
- Trustworthy
- Professional
- Modern
- Efficient

---

# 3. Color Palette

Use a sophisticated legal-tech color palette.

| Color Name | Hex Code | Usage |
|---|---|---|
| Deep Navy | #0F172A | Primary background and headings |
| Royal Blue | #2563EB | Primary buttons and actions |
| Light Blue | #DBEAFE | Secondary backgrounds |
| White | #FFFFFF | Main content surfaces |
| Slate Gray | #64748B | Secondary text |
| Light Gray | #F1F5F9 | Page backgrounds |
| Success Green | #16A34A | Successful classification |
| Warning Amber | #F59E0B | Warnings and uncertain results |
| Error Red | #DC2626 | Errors and validation messages |

### Color Usage Guidelines

- Use Deep Navy for branding and important headings.
- Use Royal Blue for primary actions.
- Use White for cards and content sections.
- Use Light Gray for the overall application background.
- Use Green for successful operations.
- Use Amber for warnings and low-confidence predictions.
- Use Red only for errors and critical alerts.

Maintain sufficient contrast between text and backgrounds.

---

# 4. Typography

Use modern, readable fonts.

### Primary Font
Inter

### Secondary Font
Roboto

### Typography Scale

| Element | Font Size | Weight |
|---|---|---|
| Main Heading | 32px | Bold |
| Section Heading | 24px | Semibold |
| Card Heading | 18px | Semibold |
| Body Text | 14px–16px | Regular |
| Labels | 13px–14px | Medium |
| Small Text | 12px | Regular |

Use consistent typography throughout the application.

---

# 5. Application Layout

The application should follow a clean dashboard-based layout.

### Main Layout Components

1. Sidebar Navigation
2. Top Header
3. Main Content Area
4. Document Upload Section
5. Classification Result Section
6. Footer

### Sidebar Navigation

The sidebar should contain:

- LexiClass AI Logo
- Dashboard
- Classify Document
- Classification History
- About Project
- Settings

The active navigation item should be highlighted using Royal Blue.

### Top Header

The top header should contain:

- Current page title
- Short page description
- User profile area (optional)

---

# 6. Dashboard Design

The dashboard should provide an overview of the application's functionality.

### Dashboard Components

**Welcome Section**

Heading: "Welcome to LexiClass AI"

Description: "Intelligently classify legal documents using AI-powered text analysis."

**Statistics Cards**

Display relevant application statistics:

- Total Documents Processed
- Successful Classifications
- Available Legal Categories
- Model Accuracy

Only display real values supported by the application's data.

**Quick Action**

Provide a prominent button:

"Classify New Document"

This button should navigate to the document classification page.

---

# 7. Document Upload Interface

This is the most important section of the application.

### Upload Card

The upload section should contain:

- Upload icon
- Heading: "Upload Your Legal Document"
- Description: "Upload a PDF or DOCX file to identify its legal category."
- Drag-and-drop upload area
- Browse Files button
- Supported file format information

### Upload Design

The upload area should have:

- Dashed border
- Rounded corners
- Light Blue background
- Upload icon
- Clear interaction feedback

### Upload States

1. Default: Show upload instructions.
2. Hover: Highlight the upload area.
3. Uploading: Display processing indicator.
4. Success: Display uploaded filename.
5. Error: Display a clear error message.

---

# 8. Classification Result Interface

After processing a document, display the prediction in a clear result card.

### Result Card Components

- Document Name
- Predicted Legal Category
- Classification Confidence (if supported by the model)
- Processing Status
- New Classification Button

### Legal Category Labels

| Category | Display Label |
|---|---|
| Criminal Law | Criminal Law |
| Civil Law | Civil Law |
| Constitutional Law | Constitutional Law |
| Property Law | Property Law |
| Other | Other Legal Domains |

Use a consistent badge style for each category.

The predicted category should be the most visually prominent information.

Do not present model confidence as guaranteed correctness.

---

# 9. Classification History

Create a history section where previously processed documents can be viewed.

### History Table

| Document Name | Predicted Category | Date | Status |
|---|---|---|---|
| Case_01.pdf | Criminal Law | Date | Completed |
| Contract_02.pdf | Civil Law | Date | Completed |

### Features

- View previous classification results.
- Search document names.
- Filter by legal category.
- Display processing status.

Only show actual stored records.

---

# 10. UI Components

Use consistent reusable components throughout the application.

### Buttons

**Primary Button**
- Background: #2563EB
- Text: #FFFFFF
- Rounded corners
- Hover: Slightly darker blue

**Secondary Button**
- Background: #FFFFFF
- Border: #CBD5E1
- Text: #0F172A

**Danger Button**
- Background: #DC2626
- Text: #FFFFFF

### Cards

- White background
- Subtle shadow
- 12px border radius
- 20px padding
- Consistent spacing

### Input Fields

- White background
- Light gray border
- Rounded corners
- Clear focus state
- Helpful validation messages

---

# 11. Responsive Design

The application must work on:

- Desktop computers
- Laptops
- Tablets
- Mobile devices

### Desktop

- Fixed sidebar
- Wide main content area
- Dashboard statistics in a horizontal grid

### Tablet

- Collapsible sidebar
- Flexible card layouts
- Responsive content spacing

### Mobile

- Compact navigation
- Single-column layout
- Full-width upload section
- Mobile-friendly buttons
- Scrollable history table

---

# 12. Icons and Visual Elements

Use Lucide icons or Streamlit-compatible icons.

Suggested icons:

| Feature | Icon |
|---|---|
| Dashboard | Layout Dashboard |
| Document Upload | File Up |
| Legal Documents | File Text |
| AI Classification | Brain Circuit |
| History | History |
| Settings | Settings |
| Success | Check Circle |
| Error | Alert Circle |

Use icons consistently and avoid unnecessary decorative graphics.

---

# 13. Animations and Interactions

Keep animations minimal and purposeful.

Recommended interactions:

- Smooth button hover transitions.
- Upload area highlighting.
- Loading spinner during document processing.
- Success feedback after classification.
- Clear error notifications.

Avoid excessive animation and distracting effects.

---

# 14. Accessibility Guidelines

- Maintain readable font sizes.
- Use sufficient color contrast.
- Provide descriptive labels for upload controls.
- Do not communicate status using color alone.
- Make navigation keyboard-friendly.
- Display clear error messages.
- Use understandable language.

---

# 15. Technical Design Guidelines

The UI should be implemented using Python and Streamlit.

### Recommended Structure

- `app.py`: Main application interface.
- `src/text_extraction.py`: Document text extraction.
- `src/data_preprocessing.py`: NLP preprocessing.
- `src/feature_extraction.py`: TF-IDF feature extraction.
- `src/model_training.py`: Model training.
- `src/prediction.py`: Document classification.

### UI Implementation Requirements

- Use reusable Streamlit components where practical.
- Separate UI logic from machine learning logic.
- Keep the application responsive.
- Display loading and error states.
- Never expose internal model files or sensitive server paths to users.
- Validate uploaded files before processing.

---

# 16. Overall User Experience

The ideal user journey should be simple:

1. User opens LexiClass AI.
2. User views the dashboard.
3. User selects Classify Document.
4. User uploads a legal document.
5. System processes the document.
6. AI model predicts the legal category.
7. User views the classification result.
8. User can classify another document.

The entire experience should feel simple, fast, reliable, and professional.

---

# 17. Final Design Goal

LexiClass AI should look and feel like a modern legal technology platform rather than a basic college-level machine learning demonstration.

The interface must balance professional legal branding with modern AI-inspired visual design.

**Core Design Principle:**

"Professional Legal Intelligence. Simple User Experience."