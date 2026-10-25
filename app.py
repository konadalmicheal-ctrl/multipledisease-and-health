import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-before-deployment')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///disease_portal.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB upload limit
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(app.instance_path, 'reports'))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('COOKIE_SECURE', '0') == '1'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessments = db.relationship('Assessment', backref='user', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('HealthReport', backref='user', lazy=True, cascade='all, delete-orphan')

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    condition = db.Column(db.String(80), nullable=False)
    risk_level = db.Column(db.String(40), nullable=False)
    notes = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False, unique=True)
    report_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(300), nullable=False, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

# Educational symptom checklist only. This is not a clinically validated ML model.
SYMPTOMS = {
    'Diabetes risk': ['frequent_thirst', 'frequent_urination', 'fatigue', 'blurred_vision'],
    'Heart health warning signs': ['chest_discomfort', 'breathlessness', 'unusual_fatigue', 'dizziness'],
    'Respiratory infection indicators': ['cough', 'fever', 'sore_throat', 'breathlessness'],
    'Anemia indicators': ['fatigue', 'dizziness', 'pale_skin', 'breathlessness'],
    'Migraine indicators': ['headache', 'light_sensitivity', 'nausea', 'sound_sensitivity'],
}
SYMPTOM_LABELS = {
 'frequent_thirst':'Frequent thirst','frequent_urination':'Frequent urination','fatigue':'Unusual fatigue',
 'blurred_vision':'Blurred vision','chest_discomfort':'Chest discomfort','breathlessness':'Breathlessness',
 'unusual_fatigue':'Unusual fatigue','dizziness':'Dizziness','cough':'Cough','fever':'Fever',
 'sore_throat':'Sore throat','pale_skin':'Paler-than-usual skin','headache':'Headache',
 'light_sensitivity':'Sensitivity to light','nausea':'Nausea','sound_sensitivity':'Sensitivity to sound'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if len(name) < 2 or len(name) > 100 or '@' not in email or len(password) < 8:
            flash('Enter a valid name/email and a password of at least 8 characters.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'error')
        else:
            user = User(name=name, email=email, password_hash=generate_password_hash(password))
            db.session.add(user); db.session.commit()
            login_user(user); flash('Account created successfully.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        user=User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash,password):
            login_user(user); return redirect(url_for('dashboard'))
        flash('Email or password is incorrect.', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user(); flash('You have been logged out.', 'success'); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent=Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', recent=recent)

@app.route('/assessment', methods=['GET','POST'])
@login_required
def assessment():
    if request.method == 'POST':
        selected=request.form.getlist('symptoms')
        if not selected:
            flash('Select at least one symptom or return to the dashboard.', 'error')
            return redirect(url_for('assessment'))
        ranked=[]
        for condition, symptoms in SYMPTOMS.items():
            matches=len(set(selected).intersection(symptoms))
            if matches: ranked.append((matches/len(symptoms), condition, matches, len(symptoms)))
        ranked.sort(reverse=True)
        score, condition, matches, total=ranked[0]
        risk='More indicators selected' if score >= .75 else ('Some indicators selected' if score >= .5 else 'Few indicators selected')
        safe_notes='Selected indicators: ' + ', '.join(SYMPTOM_LABELS.get(s,s) for s in selected if s in SYMPTOM_LABELS)
        record=Assessment(user_id=current_user.id, condition=condition, risk_level=risk, notes=safe_notes)
        db.session.add(record); db.session.commit()
        return render_template('result.html', record=record, score=round(score*100))
    return render_template('assessment.html', symptoms=SYMPTOM_LABELS)

@app.route('/history')
@login_required
def history():
    records=Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).all()
    return render_template('history.html', records=records)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if len(name) < 2 or len(name) > 100:
            flash('Name must be between 2 and 100 characters.', 'error')
        else:
            current_user.name = name
            db.session.commit()
            flash('Profile updated.', 'success')
            return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'application': 'Multiple Disease Prediction System (No AI)', 'mode': 'educational-demo'}), 200

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Safe scaffold only: no email provider or reset-token workflow is configured.
        flash('Password reset email is not configured in this demo. Contact the project administrator.', 'error')
    return render_template('forgot_password.html')

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    allowed = {'.pdf', '.png', '.jpg', '.jpeg', '.webp'}
    if request.method == 'POST':
        file = request.files.get('report_file')
        description = request.form.get('description', '').strip()[:300]
        if not file or not file.filename:
            flash('Choose a PDF or image file first.', 'error')
            return redirect(url_for('reports'))
        original = secure_filename(file.filename)
        ext = os.path.splitext(original)[1].lower()
        if ext not in allowed:
            flash('Only PDF, PNG, JPG, JPEG, and WEBP files are accepted.', 'error')
            return redirect(url_for('reports'))
        stored = f"{uuid.uuid4().hex}{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], stored))
        row = HealthReport(user_id=current_user.id, original_name=original, stored_name=stored,
                           report_type='PDF' if ext == '.pdf' else 'Image', description=description)
        db.session.add(row); db.session.commit()
        flash('Report uploaded to your account.', 'success')
        return redirect(url_for('reports'))
    items = HealthReport.query.filter_by(user_id=current_user.id).order_by(HealthReport.created_at.desc()).all()
    return render_template('reports.html', reports=items)

@app.route('/reports/<int:report_id>/download')
@login_required
def download_report(report_id):
    report = HealthReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    return send_from_directory(app.config['UPLOAD_FOLDER'], report.stored_name,
                               as_attachment=True, download_name=report.original_name)

@app.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = HealthReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    path = os.path.join(app.config['UPLOAD_FOLDER'], report.stored_name)
    try:
        if os.path.isfile(path): os.remove(path)
    finally:
        db.session.delete(report); db.session.commit()
    flash('Report deleted from your account.', 'success')
    return redirect(url_for('reports'))

@app.errorhandler(413)
def too_large(_):
    flash('File is too large. Maximum upload size is 8 MB.', 'error')
    return redirect(url_for('reports'))

@app.route('/health-library')
def health_library():
    articles=[
      ('Diabetes awareness','Learn about common signs such as increased thirst, frequent urination and fatigue. Screening and diagnosis require qualified health professionals.'),
      ('Heart health','Seek emergency care for severe chest pain, sudden breathing difficulty or fainting. Risk factors should be discussed with a clinician.'),
      ('Respiratory health','Rest, hydration and hygiene can help with many mild illnesses. Persistent or worsening symptoms need medical advice.'),
      ('Anemia awareness','Fatigue and dizziness can have many causes. A clinician may recommend blood tests to check for anemia.'),
      ('Migraine awareness','Headache with light or sound sensitivity may occur for several reasons. A clinician can help assess recurring or severe headaches.'),
    ]
    return render_template('health_library.html', articles=articles)

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html', users=User.query.order_by(User.created_at.desc()).all(), assessments=Assessment.query.count(), report_count=HealthReport.query.count())

@app.errorhandler(403)
def forbidden(_): return render_template('error.html', code=403, message='You do not have permission to view this page.'), 403
@app.errorhandler(404)
def not_found(_): return render_template('error.html', code=404, message='The page you requested was not found.'), 404

with app.app_context():
    db.create_all()
    # Optional first admin account. Set both environment variables before first launch.
    admin_email=os.environ.get('ADMIN_EMAIL','').strip().lower()
    admin_password=os.environ.get('ADMIN_PASSWORD','')
    if admin_email and admin_password and not User.query.filter_by(email=admin_email).first():
        db.session.add(User(name='Administrator', email=admin_email, password_hash=generate_password_hash(admin_password), role='admin'))
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
