# Multiple Disease Prediction System (No AI Assistant)

A responsive Flask web application for a college project. It includes account registration/login, a personal dashboard, an educational symptom checklist for several health topics, assessment history, a health information library, private report upload/download/delete (PDF and images), a Google Lens external-link helper, and a separate admin page, editable display-name profile, privacy page, health endpoint, and password-reset placeholder (email reset is not configured). **There is no chatbot or external AI/API integration.**

## Important medical limitation
The symptom checklist uses simple, transparent rule-based matching for demonstration. It is **not** a trained or clinically validated prediction model, cannot diagnose disease, and must not be used for treatment decisions. A real clinical prediction system requires suitable validated datasets, model evaluation, clinical oversight, privacy review, and regulatory review where applicable. Emergency symptoms require urgent local medical help.

## Features
- Register, login and logout; passwords stored as hashes
- Individual account and assessment history
- Responsive home page, dashboard, and forms
- Educational indicators for diabetes, heart-health warning signs, respiratory infection, anemia and migraine
- Health library with general awareness information
- Admin-only overview page
- SQLite for local development; PostgreSQL supported through `DATABASE_URL`
- Gunicorn entry point and hosting configuration
- Basic security settings and environment-variable configuration

## Additional account/privacy features
- Profile display-name editing, a privacy information page, and `/health` status endpoint are included.
- Forgot-password page is only a placeholder; email delivery and secure reset tokens are not configured.

## Report uploads and Google Lens
- Signed-in users can upload PDF, PNG, JPG/JPEG, and WEBP sample reports (8 MB maximum), then download or delete their own files.
- A Google Lens link opens the external Google Lens website; Lens is not embedded and does not automatically receive private uploaded reports.
- On a public host, configure a persistent private upload volume or private object storage. The default local upload directory may be ephemeral on some hosts. Never upload real patient information for a college demo.

## Run locally (Windows)
1. Install Python 3.11 or newer from python.org and enable **Add Python to PATH**.
2. Extract the ZIP and open the extracted project folder in Command Prompt/PowerShell.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt and run `.venv\\Scripts\\activate.bat`.
4. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Create a `.env` file by copying `.env.example`. Set a long random `SECRET_KEY`. (The app does not automatically load `.env`; set environment variables in your terminal or hosting dashboard. For easiest local run, the built-in development secret works but must not be used in production.)
6. Start the site:
   ```powershell
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in your browser. Register an ordinary account to test it.

### Optional admin account (local PowerShell)
Set these before starting the app:
```powershell
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="replace-with-a-strong-password"
$env:SECRET_KEY="a-long-random-secret"
python app.py
```
The admin is created only if that email does not already exist. Log in with it, then visit `/admin`. Never commit credentials to GitHub.

## Host on the internet (Render-style deployment)
1. Create a GitHub repository and upload the project files (do **not** upload `.env`, passwords, or database files).
2. On a Python web host such as Render, create a new Web Service connected to that repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables in the hosting dashboard: `SECRET_KEY` (long random value), `DATABASE_URL` (managed PostgreSQL URL recommended), and optionally `ADMIN_EMAIL` + `ADMIN_PASSWORD` for the initial admin account. Set `COOKIE_SECURE=1` when HTTPS is configured.
6. Deploy and test registration, login, assessment submission, history, and logout on the live URL.

**Do not rely on local SQLite storage on hosts with an ephemeral filesystem.** Use managed PostgreSQL for a deployed app. Set a strong secret, use HTTPS, restrict admin credentials, and review the host's current pricing/sleep/storage limits before publishing.

## Project structure
```
Multiple_Disease_Prediction_System_No_AI/
├── app.py
├── requirements.txt
├── Procfile
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── reports.html
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── assessment.html
│   ├── result.html
│   ├── history.html
│   ├── health_library.html
│   ├── admin.html
│   └── error.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Before a real public launch
- Replace the demo checklist with a validated, documented model only if you have the right dataset and permission to use it.
- Add CSRF protection, email verification, production password reset, rate limiting, privacy notice/consent, data export/deletion, audit logs, private persistent report storage, and automated security tests before handling sensitive data.
- Avoid collecting real patient information in a student demo.
