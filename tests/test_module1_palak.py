# tests/test_module1_palak.py
# Unit Test Suite for Module 1: Palak Rawat (Authentication & Dashboard)

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User


class TestModule1Palak(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Clean any leftover test users
        User.query.filter(User.username.like('test_palak_%')).delete()
        db.session.commit()

    def tearDown(self):
        User.query.filter(User.username.like('test_palak_%')).delete()
        db.session.commit()
        self.ctx.pop()

    def test_01_register_page_loads(self):
        res = self.client.get('/auth/register')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Create Account", res.data)

    def test_02_login_page_loads(self):
        res = self.client.get('/auth/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Smart Hospital System", res.data)

    def test_03_register_user_success(self):
        res = self.client.post('/auth/register', data={
            'username': 'test_palak_nurse',
            'password': 'password123',
            'userRole': 'Doctor'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Registration Successful", res.data)

        user = User.query.filter_by(username='test_palak_nurse').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.user_role, 'Doctor')

    def test_04_duplicate_registration_rejected(self):
        self.client.post('/auth/register', data={
            'username': 'test_palak_dupe',
            'password': 'password123',
            'userRole': 'Admin'
        })
        res = self.client.post('/auth/register', data={
            'username': 'test_palak_dupe',
            'password': 'password456',
            'userRole': 'Admin'
        }, follow_redirects=True)
        self.assertIn(b"already exists", res.data)

    def test_05_login_success_and_session_created(self):
        u = User(username='test_palak_login', user_role='Admin', login_status='Logged Out')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()

        res = self.client.post('/auth/login', data={
            'username': 'test_palak_login',
            'password': 'mypassword'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Hospital Resource Command Center", res.data)

    def test_06_login_invalid_credentials_rejected(self):
        res = self.client.post('/auth/login', data={
            'username': 'non_existent_user',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b"Invalid Username or Password", res.data)

    def test_07_dashboard_requires_login(self):
        res = self.client.get('/dashboard/', follow_redirects=False)
        self.assertIn(res.status_code, (302, 401))

    def test_08_logout_clears_session(self):
        u = User(username='test_palak_logout', user_role='Patient', login_status='Logged Out')
        u.set_password('pass123')
        db.session.add(u)
        db.session.commit()

        self.client.post('/auth/login', data={
            'username': 'test_palak_logout',
            'password': 'pass123'
        })
        res = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Logged Out Successfully", res.data)


if __name__ == '__main__':
    unittest.main()
