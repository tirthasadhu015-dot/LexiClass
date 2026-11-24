# LexiClass AI

**Smarter Legal Documents, Simplified.**

LexiClass AI is a Python and Streamlit project for classifying legal PDF and DOCX documents into Criminal Law, Civil Law, Constitutional Law, Property Law, or Other Legal Domains. The application and model pipeline are not implemented yet; no dataset or trained model is included.

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
