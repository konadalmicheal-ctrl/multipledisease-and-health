# Start Here — Telugu Simple Steps

## 1) PC lo run cheyyadam
1. ZIP ni Extract All cheyyandi.
2. Python 3.11+ install cheyyandi; install time lo Add Python to PATH tick cheyyandi.
3. Project folder lo address bar lo `cmd` type chesi Enter nokkandi.
4. Ee commands okkokkati run cheyyandi:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
5. Browser lo `http://127.0.0.1:5000` open cheyyandi. Register chesi login avvandi.
6. Dashboard nunchi checklist, history, health library, My Reports, Profile, Privacy pages try cheyyandi. `/health` endpoint ni browser lo kuda test cheyyachu.

## 2) Admin account (optional)
Command Prompt lo server start cheyyadaniki mundu credentials set cheyyali. Example PowerShell:
```powershell
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="Use-A-Strong-Unique-Password"
$env:SECRET_KEY="Replace-With-A-Long-Random-Secret"
python app.py
```
Production admin password ni code lo/ GitHub lo rayakandi.

## 3) Google Lens and reports
- My Reports page lo PDF/JPG/PNG sample file upload, download, delete cheyyachu. Max 8 MB.
- Google Lens button external website open chestundi. Private report file automatic ga Lens ki upload avvadu.
- Demo kosam fake/sample reports matrame use cheyyandi.

## 4) Internet lo host cheyyadam
1. GitHub lo new repository create cheyyandi. `.env`, database files, `.venv` upload cheyyakandi.
2. Render lanti Python web host lo Web Service create chesi repository connect cheyyandi.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Environment variables: strong `SECRET_KEY`, persistent PostgreSQL `DATABASE_URL`, `COOKIE_SECURE=1`, and admin credentials only if you need initial admin creation.
6. Report uploads kosam private persistent disk/object storage configure cheyyandi; upload directory ni `UPLOAD_FOLDER` lo set cheyyandi.
7. Live site lo register/login, checklist, history, report upload/download/delete test cheyyandi.

**Important:** Free hosting limits/prices maaruthayi. SQLite and uploaded files konni hosts lo restart/deploy ayyaka pothayi. Public hosting ki persistent DB + persistent private file storage kavali.

## Medical safety
Idi educational student prototype. Checklist result diagnosis kaadu; real clinical prediction model kaadu. Real patient reports public demo lo upload cheyyakandi.
