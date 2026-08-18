# PROJECT_CONTEXT.md

## Project Overview

**Project name:** Solar Panel Degradation Predictor Using Machine Learning

**Purpose:** A full Phase-II academic web application that predicts solar panel efficiency degradation from environmental and operational data, supports batch and single-row prediction, generates maintenance recommendations, and exports PDF/Excel reports.

**Academic context:** VTU, BE CSE (AI&ML), Rajeev Institute of Technology, Hassan.

## Current Tech Stack

- **Backend:** Python 3.10+, Flask, Flask-Login, Werkzeug, SQLAlchemy (via Flask-SQLAlchemy), SQLite, python-dotenv, Gunicorn (production WSGI server)
- **ML:** scikit-learn, pandas, NumPy, joblib
- **Reporting:** fpdf2 (PDF generation), openpyxl (Excel generation)
- **Frontend:** Jinja2 server-rendered templates, HTML/CSS with the Plus Jakarta Sans font, a dark/light theme toggle (dark is default), Chart.js (via CDN) for the results bar chart, vanilla JS for the theme switcher
- **Offline visualization:** Matplotlib and Seaborn, used only in `ml/evaluate_model.py` to produce static PNGs in `outputs/` (predicted-vs-actual, residuals, feature importance) — not used at request time
- **Version control:** Git, GitHub
- **Deployment:** Render (persistent/long-running Flask web service, not serverless)
- **Dev environment:** VS Code, pip + `requirements.txt` (no poetry/pipenv)

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
│   └── assorted generated test/report/diagram-review outputs
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
├── archive/
│   └── MAJOR PHASE2-1.pptx, MAJOR PHASE2-2.pptx (superseded intermediate deck versions)
├── ARCHITECTURE.md
├── README.md
├── requirements.txt
├── render.yaml
├── run.py
├── MAJOR PHASE2-2_FINAL.pptx        (current, corrected 16-slide deck)
└── PRESENTATION_SCRIPT.pdf          (rehearsal script for the final deck)
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
- **PDF/Excel styling has since been updated to match the web theme** (navy header, amber labels, severity-tinted cells/rows) — see `THEME_COLORS_RGB`/`THEME_COLORS_HEX`/`SEVERITY_TINT_*` in `report_generator.py`. This was outstanding at an earlier point in the project but is now complete.

### Phase 5 - Hardening, Documentation, and Delivery Prep
- `README.md` expanded with local setup and troubleshooting guidance
- `ARCHITECTURE.md` created to map implementation back to Phase-I architecture
- `.env.example` reduced to only the environment variables actually used
- Git repository initialized and pushed to GitHub after removing oversized model artifact from commit history
- Visual redesign pass completed across the web UI without changing backend behavior

### Phase 6 - Email Login and Theme System (added after the original Phase 1-5 write-up)
- `User` model now has a unique, indexed, required `email` column alongside `username`
- Registration requires and validates the email field: non-empty, basic format check (`^[^@\s]+@[^@\s]+\.[^@\s]+$`), and uniqueness check (same pattern as the existing username uniqueness check)
- Login keeps a single input field, relabeled "Username or Email": the lookup tries `username` first, then falls back to `email` (lowercased) if no username match is found
- Dark/light theme system added to `base.html`:
  - Dark mode is the default on first load (an inline script in `<head>` sets `data-theme="dark"` before any content paints, avoiding a flash of the wrong theme)
  - A toggle button in the navbar switches themes; the choice is persisted in `localStorage` under the key `theme` and restored on next visit
  - All colors are defined as CSS custom properties on `:root` (dark values) with overrides under `html[data-theme="light"]` (see "Design System" below for exact values)

### Phase 7 - Deployment Fixes (Render)
- Live deployment completed on Render (see "Current Deployment Status")
- Fixed a Render build failure caused by a NumPy major-version mismatch between the local training environment and Render's installed dependencies (`No module named 'numpy._core'`), by pinning `numpy==2.4.4` (a 2.x release compatible with Render's Python 3.11, avoiding both the 1.x/2.x unpickling break and the `numpy==2.5.1` "requires Python >=3.12" build failure)
- Enabled `SESSION_COOKIE_SECURE = True` in `ProductionConfig` so session cookies are only sent over HTTPS in production

## Current Verification Status

- End-to-end user flow works: register, login, dashboard, upload, batch results, manual prediction, history
- Report endpoints work and return valid authenticated PDF and Excel responses
- Upload processing bug related to already-cleaned datasets has been fixed
- Live Render deployment has been verified end-to-end (register → login → CSV upload → batch prediction) using a fresh test account
- Full local smoke-test screenshot set is complete: `screenshots/01_register.png` through `screenshots/10_excel_report.png`, all captured under the presentable `solar_admin` account. The PDF/Excel report screenshots were produced by downloading the real authenticated report files and rendering them to PNG (PyMuPDF for the PDF, Excel COM export-to-PDF plus PyMuPDF for the Excel workbook), since the embedded browser's download-event capture is unreliable for attachment endpoints.
- Hero/banner text contrast is verified readable after the redesign fixes

## Current Design System

### Typography
- Font family: Plus Jakarta Sans
- Body text: weight 400
- Navigation and form labels: weight 500-600
- Buttons: weight 600
- Headings (`h1`, `h2`, `h3`): weight 700
- Major prediction values (large efficiency score): weight 800

### Theme System (Dark Default, Light Toggle)
All colors are CSS custom properties defined once on `:root` for dark mode, with a light-mode override block under `html[data-theme="light"]`. The active theme is stored in `localStorage` and applied before first paint.

**Dark mode (default) — from `app/templates/base.html` `:root`:**
- `--navy: #0F1729` — primary dark navy accent
- `--navy-soft: #17233d`
- `--surface: #0B1220` — page background
- `--surface-strong: #141B2D`
- `--surface-edge: #0E1629`
- `--border: #1E293B`
- `--text: #F1F5F9`
- `--heading: #F1F5F9`
- `--label: #CBD5E1`
- `--muted: #94A3B8` / `--hero-subtitle: #94A3B8`
- `--amber: #F59E0B` (primary CTA / warning) / `--amber-deep: #d97706`
- `--blue: #3B82F6` (links, info state, chart palette)
- `--green: #22C55E` (success / healthy efficiency states)
- `--red: #EF4444` (error / critical efficiency states)
- `--card-bg: #141B2D`, `--card-border: #1E293B`, `--panel-bg: #141B2D`
- `--input-bg: rgba(11, 18, 32, 0.85)`, `--input-bg-focus: rgba(15, 23, 41, 0.95)`
- `--table-header-bg: rgba(30, 41, 59, 0.8)`, `--table-header-text: #E2E8F0`
- `--button-secondary-bg: #1F2937`, `--button-secondary-text: #E2E8F0`, `--button-secondary-border: #334155`

**Light mode override — from `html[data-theme="light"]`:**
- `--surface: #F8FAFC`, `--surface-strong: #ffffff`, `--surface-edge: #E4E9F2`
- `--border: #dbe4f0`
- `--text: #0f1729`, `--heading: #0F1729`, `--label: #0F1729`, `--muted: #5b6b83`
- `--bg-mid: #F1F5FB`
- `--card-bg: rgba(255, 255, 255, 0.92)`, `--card-border: rgba(255, 255, 255, 0.72)`
- `--input-bg: rgba(248, 250, 252, 0.92)`, `--input-bg-focus: #ffffff`
- `--table-header-bg: #EEF2F9`, `--table-header-text: #0F1729`
- `--button-secondary-bg: rgba(15, 23, 41, 0.08)`, `--button-secondary-text: #0F1729`
- (`--navy`, `--amber`, `--blue`, `--green`, `--red` are not overridden in light mode — they keep their dark-mode values as brand/status accents in both themes)

### Surface Treatment
- Page background is a tinted gradient, not flat white/black, in both themes
- Main cards use translucent backgrounds over the tinted page background
- Cards and panels use left-border accents by content category
- Hover elevation is applied to card-like surfaces
- Dashboard "Model Snapshot / About This System" card is intentionally dark navy as the page anchor in both themes
- Results efficiency panel uses a soft status-tinted background based on severity
- Table headers use a navy-tinted background rather than neutral gray

## Maintenance Recommendation Thresholds

Implemented in `app/utils/maintenance_rules.py`, evaluated in priority order:

1. **`predicted_efficiency < 0.40`** → *"Urgent maintenance required — efficiency critically low"* (severity: `critical`)
2. **`0.40 <= predicted_efficiency <= 0.55` AND `soiling_ratio > 0.75`** → *"Schedule panel cleaning — high soiling detected"* (severity: `warning`)
3. **`panel_age > 25` AND `predicted_efficiency < 0.55`** → *"Inspect for age-related degradation"* (severity: `warning`)
4. **Otherwise** → *"No immediate maintenance needed — monitor periodically"* (severity: `ok`)

**Reasoning (from code comments and EDA):**
- `0.40` is used as the critical cutoff because the dataset's mean efficiency is roughly `0.51`–`0.53`; below `0.40` a panel is meaningfully below the normal operating distribution, not just slightly under average.
- `0.75` soiling ratio marks heavily dirty panels, where cleaning is a low-cost, high-impact fix rather than a sign of deeper hardware degradation.
- `25` years reflects typical expected panel lifespan; combined with sub-`0.55` efficiency, an older panel in that state is treated as a physical-inspection candidate rather than a cleaning candidate.

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
- In the integrated automated browser tooling used for smoke testing, PDF/Excel attachment endpoints do not reliably expose a capturable "download" event, which blocked capturing `09_pdf_report.png`/`10_excel_report.png` in the most recent smoke-test pass.
- Earlier smoke tests worked around this by verifying those endpoints through authenticated in-page requests instead of relying on the browser's native download flow.

### Render NumPy Version Mismatch (resolved)
- The first Render deploy failed at runtime with `No module named 'numpy._core'` because the local model artifacts were pickled under a different NumPy major version than what Render initially installed.
- A follow-up attempt to pin `numpy==2.5.1` then failed at Render's *build* step (`Requires-Python >=3.12`) because Render's Python was 3.11.
- Resolved by pinning `numpy==2.4.4`, a NumPy 2.x release compatible with Python 3.11, which avoided both the 1.x/2.x unpickling incompatibility and the Python-version build failure. Verified by a successful live upload on the deployed Render service.

## Runtime and Model Details

- Best runtime model: Gradient Boosting Regressor
- Saved model used by web app: `models/best_model.joblib`
- Feature schema source: `models/feature_columns.joblib`
- `random_forest.joblib` is not part of the repository
- Batch upload accepts both raw CSV shape and already-cleaned model-ready CSV shape
- Maintenance recommendation logic is rule-based and intentionally explainable
- Model comparison metrics: Linear Regression R²=0.7531/RMSE=0.0521/MAE=0.0394; Random Forest R²=0.7791/RMSE=0.0493/MAE=0.0372; **Gradient Boosting (selected)** R²=0.7900/RMSE=0.0480/MAE=0.0362
- Irradiance confirmed as the dominant feature: importance ≈0.674, matching an EDA correlation of ≈+0.74 with efficiency

## Current Deployment Status

- GitHub repository (primary/origin): https://github.com/techWithKeerthana/solar-panel-degradation-predictor.git
- A second remote also exists locally, named `friend`, pointing to a collaborator's fork: https://github.com/sinchanaar01/solar-panel-degradation-predictor.git
- Live deployment: **completed** on Render at `https://solar-panel-degradation-predictor-ssrn.onrender.com` (verified live: registration, login, and CSV batch upload all confirmed working end-to-end on the deployed service)
- Deployment config: `render.yaml` at repo root — Python web service, `buildCommand: pip install -r requirements.txt`, `startCommand: gunicorn "app.app:create_app('production')" --bind 0.0.0.0:$PORT`
- Render environment variables expected in the dashboard: `SECRET_KEY`, `FLASK_ENV=production`, `DATABASE_URL` (optional override)
- `SESSION_COOKIE_SECURE = True` is set in `ProductionConfig`, so production session cookies require HTTPS (confirmed not to cause a login loop on the live HTTPS deployment)
- Reason Render was chosen over Vercel: this is a stateful Flask app using SQLite and local file storage patterns; Render supports a conventional long-running Python web service model, while Vercel's serverless model would require architecture changes around persistence and file handling
- Free-tier caveat: Render's free-tier filesystem is ephemeral, so `instance/app.db` and `uploads/` can reset on redeploy/restart — this affects persistence guarantees, not correctness of the deployed code

## PPT / Presentation Status

- **Current deck:** `MAJOR PHASE2-2_FINAL.pptx` (16 slides) is the corrected, presentation-ready version. It contains:
  - An accurate 8-step **Methodology** diagram (native PowerPoint shapes, not an image): data collection → preprocessing (no scaling) → EDA → training exactly 3 models → evaluation & selection → prediction (load `best_model.joblib`, inference only) → maintenance recommendation → results & reports
  - An accurate **Data Flow Diagram** (native PowerPoint shapes): User (single account type, no role hierarchy) → Input Interface → Application Layer (`auth.py`, `dataset.py`, `predict.py`, `reports.py`) → Data Processing → ML Model (inference only, no retrain) → Prediction Engine → Outputs (PDF **and** Excel); only the Application Layer connects to the SQLite Data Store, and trained models are explicitly noted as files on disk, not database rows
  - A **Result and Outcome** slide with a real results table (Linear Regression / Random Forest / Gradient Boosting, with R²/RMSE/MAE) and the irradiance dominant-feature note
  - A **System Implementation** slide with a feature bullet list (Authentication, Batch Upload, Manual Prediction, Reports, Maintenance Rules, Live Deployment) and two real screenshots from the deployed dark-theme app, captioned "Live Dashboard" and "Prediction Result"
  - Literature Survey slides moved ahead of Objectives per guide feedback, with the Contents/roadmap slide updated to match
- **Rehearsal script:** `PRESENTATION_SCRIPT.pdf` — a full slide-by-slide spoken script (not just bullet restatement) with a suggested 4-way speaking split, pacing/emphasis cues, proactively-explained technical reasoning for the Methodology/Data Flow/Result/Implementation slides, and an Anticipated Questions section grounded in this file, `ARCHITECTURE.md`, and the actual debugging history (e.g. the Render NumPy fix)
- The superseded `MAJOR PHASE2-1.pptx` and `MAJOR PHASE2-2.pptx` versions have been moved to `archive/` so the repo root only contains the current, presentation-ready `MAJOR PHASE2-2_FINAL.pptx`

## Outstanding Work

- Render's free-tier ephemeral filesystem means SQLite/file-storage persistence should be reviewed further if this needs to survive redeploys reliably (e.g. moving to Render Postgres or another persistent store)
- Beyond the deployment fixes above, the broader production-hardening gaps are already tracked in detail in `ARCHITECTURE.md` (no role hierarchy, no external email/alerting/cloud-backup services, no rate limiting, no full CSRF-token framework, no encryption at rest, no structured audit logging) — those remain intentionally out of scope for this academic Phase-II submission

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
