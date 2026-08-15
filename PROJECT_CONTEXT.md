# PROJECT_CONTEXT.md

## Project Overview

**Project name:** Solar Panel Degradation Predictor Using Machine Learning

**Purpose:** A full Phase-II academic web application that predicts solar panel efficiency degradation from environmental and operational data, supports batch and single-row prediction, generates maintenance recommendations, and exports PDF/Excel reports.

**Academic context:** VTU, BE CSE (AI&ML), Rajeev Institute of Technology, Hassan.

## Current Tech Stack

- Backend: Python, Flask
- Auth/session management: Flask-Login
- Database: SQLite with Flask-SQLAlchemy / SQLAlchemy
- ML/data stack: pandas, numpy, scikit-learn, joblib
- Reporting: fpdf2 for PDF, openpyxl for Excel
- Visualization in web UI: Chart.js via CDN
- Frontend: Jinja2 server-rendered HTML templates with shared CSS in `app/templates/base.html`
- Environment loading: python-dotenv via `load_dotenv()` in `run.py`
- Version control: Git, GitHub

## Current Folder Structure

```text
Major_Project/
├── .env
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── models_db.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dataset.py
│   │   ├── predict.py
│   │   └── reports.py
│   ├── static/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── history.html
│   │   ├── login.html
│   │   ├── predict.html
│   │   ├── register.html
│   │   ├── results.html
│   │   ├── upload.html
│   │   └── upload_results.html
│   └── utils/
│       ├── __init__.py
│       ├── maintenance_rules.py
│       └── report_generator.py
├── data/
│   ├── train.csv
│   └── train_cleaned.csv
├── instance/
│   └── app.db
├── ml/
│   ├── evaluate_model.py
│   ├── predict.py
│   ├── preprocessing.py
│   └── train_model.py
├── models/
│   ├── best_model.joblib
│   ├── feature_columns.joblib
│   ├── gradient_boosting.joblib
│   └── linear_regression.joblib
├── notebooks/
│   └── eda_cleaning.ipynb
├── outputs/
│   ├── feature_importance.png
│   ├── predicted_vs_actual.png
│   ├── residuals.png
│   └── assorted generated test/report outputs
├── screenshots/
│   ├── 01_register.png
│   ├── 02_login.png
│   ├── 03_dashboard.png
│   ├── 04_upload.png
│   ├── 05_upload_results.png
│   ├── 06_predict_form.png
│   ├── 07_predict_results.png
│   ├── 08_history.png
│   ├── 09_pdf_report.png
│   └── 10_excel_report.png
├── src/
├── uploads/
│   └── per-user uploaded CSVs and generated prediction CSVs
├── ARCHITECTURE.md
├── README.md
├── requirements.txt
└── run.py
```

## What Has Been Built

### Phase 1 - Machine Learning Core
- Reusable preprocessing pipeline extracted into `ml/preprocessing.py`
- Training/evaluation scripts created in `ml/train_model.py` and `ml/evaluate_model.py`
- Three models compared: Linear Regression, Random Forest Regressor, Gradient Boosting Regressor
- Best runtime model is Gradient Boosting
- Model artifacts saved to `models/`
- Canonical feature schema persisted in `models/feature_columns.joblib`
- Evaluation plots generated in `outputs/`

### Phase 2 - Database and Authentication
- SQLite-backed persistence implemented through SQLAlchemy models in `app/models_db.py`
- `User`, `Dataset`, and `PredictionResult` models created
- Registration, login, logout, and dashboard routes implemented in `app/routes/auth.py`
- Password hashing handled with Werkzeug
- Session handling handled with Flask-Login

### Phase 3 - Prediction Workflow
- Dataset upload route implemented in `app/routes/dataset.py`
- Manual single-row prediction route implemented in `app/routes/predict.py`
- Prediction history view implemented
- Model loaded at runtime instead of retraining on requests
- Maintenance recommendation rules implemented in `app/utils/maintenance_rules.py`

### Phase 4 - Reporting
- PDF report generation implemented in `app/utils/report_generator.py`
- Excel report generation implemented in `app/utils/report_generator.py`
- Authenticated download routes implemented in `app/routes/reports.py`
- Ownership checks enforced so users can only download their own reports

### Phase 5 - Hardening, Documentation, and Delivery Prep
- `README.md` expanded with local setup and troubleshooting guidance
- `ARCHITECTURE.md` created to map implementation back to Phase-I architecture
- `.env.example` reduced to only the environment variables actually used
- Git repository initialized and pushed to GitHub after removing oversized model artifact from commit history
- Visual redesign pass completed across the web UI without changing backend behavior

## Current Verification Status

- End-to-end user flow works: register, login, dashboard, upload, batch results, manual prediction, history
- Report endpoints work and return valid authenticated PDF and Excel responses
- Upload processing bug related to already-cleaned datasets has been fixed
- Current smoke test screenshots exist in `screenshots/01_register.png` through `screenshots/10_excel_report.png`
- Hero/banner text contrast is verified readable after the redesign fixes

## Current Design System

### Typography
- Font family: Plus Jakarta Sans
- Body text: weight 400
- Navigation and form labels: weight 500-600
- Buttons: weight 600
- Headings (`h1`, `h2`, `h3`): weight 700
- Major prediction values (large efficiency score): weight 800

### Color Roles
- Primary dark navy: `#0F1729`
  - Hero background
  - Navbar background
  - Dark anchor card on dashboard
  - Dark CTA variant
  - Table/card accent option
- Off-white base surface: `#F8FAFC`
  - Hero title color
  - Light page surface start
  - Light card surfaces
- Page background edge tint: `#E4E9F2`
  - Shared page background gradient edge/end color
- Mid background blend: `#F1F5FB`
  - Shared page background gradient mid-stop
- Solar amber: `#F59E0B`
  - Primary CTA
  - Data Intake accent border
  - Warning state
  - Dashboard dark card highlight text
- Supporting blue: `#3B82F6`
  - Links
  - Inference/Exports accents
  - Info state
  - Chart palette
  - Dashboard dark card highlight text
- Status green: `#22C55E`
  - Good/healthy efficiency states
  - Traceability accent border
  - Success messages
- Status red: `#EF4444`
  - Critical efficiency states
  - Error messages
  - Critical severity tinting
- Hero subtitle color: `#94A3B8`
  - Subtitle text on navy hero background

### Surface Treatment
- Page background is a light gradient, not flat white
- Main cards use near-white translucent backgrounds over the tinted page background
- Cards and panels use left-border accents by content category
- Hover elevation is applied to card-like surfaces
- Dashboard "Model Snapshot / About This System" card is intentionally dark navy as the page anchor
- Results efficiency panel uses a soft status-tinted background based on severity
- Table headers use a navy-tinted light background rather than neutral gray

## Current Routes

- `/register`
- `/login`
- `/logout`
- `/dashboard`
- `/upload`
- `/upload/results`
- `/predict`
- `/results/<id>`
- `/history`
- `/reports/<id>/pdf`
- `/reports/<id>/excel`

## Known Quirks and Gotchas

### Windows Flask Debug Reloader
- On Windows, stopping the Flask debug server with Ctrl+C can leave orphaned `python.exe` processes behind due to the Werkzeug reloader parent/child process behavior.
- This was documented in the project documentation and handled operationally during testing by explicitly killing lingering processes when necessary.

### SQLite Path Resolution
- With `DATABASE_URL=sqlite:///app.db`, Flask/SQLAlchemy resolves the SQLite file under the Flask instance path, resulting in `instance/app.db`, not a database file at the repository root.
- This behavior was validated during runtime inspection and should be assumed by future work.

### Environment Loading Order
- `load_dotenv()` in `run.py` must execute before importing and constructing the Flask app.
- If app modules are imported first, environment-driven settings like `SECRET_KEY` and `DATABASE_URL` may be read too early.

### Oversized Git Artifact
- Initial push to GitHub failed because `models/random_forest.joblib` exceeded GitHub’s 100 MB file limit.
- The file was removed from tracking with `git rm --cached`, added to `.gitignore`, and the prior commit was amended before a successful push.
- The local file remains on disk, but it is intentionally excluded from the repository.

### Upload Processing Bug
- The upload path originally always re-ran raw preprocessing, which failed on already-cleaned/encoded CSVs such as `train_cleaned.csv` because raw categorical columns like `error_code` no longer existed.
- This was fixed in `app/routes/dataset.py` by detecting whether an upload is raw or already model-ready and routing it accordingly.

### Embedded Browser Download Limitation
- In the integrated browser, PDF/Excel attachment endpoints do not render as normal pages.
- During smoke tests, those endpoints were verified through authenticated in-page requests and captured with proof banners in screenshots.

## Runtime and Model Details

- Best runtime model: Gradient Boosting Regressor
- Saved model used by web app: `models/best_model.joblib`
- Feature schema source: `models/feature_columns.joblib`
- `random_forest.joblib` is not part of the repository
- Batch upload accepts both raw CSV shape and already-cleaned model-ready CSV shape
- Maintenance recommendation logic is rule-based and intentionally explainable

## Current Deployment Status

- GitHub repository: https://github.com/techWithKeerthana/solar-panel-degradation-predictor.git
- Current status: repository pushed to GitHub, not yet deployed live
- Recommended deployment target: Render
- Reason Render is recommended over Vercel:
  - Current app architecture is a stateful Flask app using SQLite and local file storage patterns
  - Render supports a conventional long-running Python web service model
  - Vercel's serverless model would require architecture changes around persistence and file handling
  - Render is the lower-friction deployment path for the code as it currently exists

## Outstanding Work

- PDF and Excel output styling has not yet been updated to match the redesigned web UI theme
- Live deployment to Render has not yet been completed
- If production deployment happens, SQLite/file-storage strategy should be reviewed for persistence guarantees on the chosen platform
- The upload processing bug is fixed and verified on the previously failing cleaned dataset
- The web UI redesign is complete for current pages and has been smoke tested with fresh screenshots

## Current Environment Variables Actually Used

- `SECRET_KEY`
- `FLASK_ENV`
- `DATABASE_URL`

## Important Files to Read First

- `README.md`
- `ARCHITECTURE.md`
- `run.py`
- `app/app.py`
- `app/config.py`
- `app/models_db.py`
- `app/routes/auth.py`
- `app/routes/dataset.py`
- `app/routes/predict.py`
- `app/routes/reports.py`
- `app/utils/maintenance_rules.py`
- `app/utils/report_generator.py`
- `ml/preprocessing.py`
- `ml/predict.py`
- `ml/train_model.py`
- `ml/evaluate_model.py`

## Current State Summary

This repository is currently a working Flask-based Phase-II academic system with:
- trained ML artifacts
- reusable preprocessing
- SQLite-backed authentication and persistence
- batch upload and single-row prediction
- history and maintenance recommendations
- PDF/Excel export
- GitHub source control
- a redesigned, production-style light dashboard theme
- fresh smoke-test screenshots confirming current behavior and visuals
