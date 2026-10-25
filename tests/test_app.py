import os
import tempfile
import unittest
from app import app, db, User
from werkzeug.security import generate_password_hash

class AppSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.tmp.close()
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SQLALCHEMY_DATABASE_URI='sqlite:///' + self.tmp.name, SECRET_KEY='test-secret')
        self.ctx=app.app_context(); self.ctx.push(); db.drop_all(); db.create_all()
        db.session.add(User(name='Test User', email='test@example.com', password_hash=generate_password_hash('testpassword123'))); db.session.commit()
        self.client=app.test_client()
    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop(); os.unlink(self.tmp.name)
    def test_home(self): self.assertEqual(self.client.get('/').status_code, 200)
    def test_register_page(self): self.assertEqual(self.client.get('/register').status_code, 200)
    def test_login_and_dashboard(self):
        response=self.client.post('/login', data={'email':'test@example.com','password':'testpassword123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200); self.assertIn(b'YOUR DASHBOARD', response.data)
    def test_protected_assessment_redirects(self): self.assertIn(self.client.get('/assessment').status_code, (302, 401))
    def test_health_library(self): self.assertEqual(self.client.get('/health-library').status_code, 200)
    def test_reports_requires_login(self): self.assertEqual(self.client.get('/reports').status_code, 302)
    def test_reports_page_after_login(self):
        self.client.post('/login', data={'email':'test@example.com','password':'testpassword123'})
        response=self.client.get('/reports')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My health reports', response.data)

if __name__ == '__main__': unittest.main()
