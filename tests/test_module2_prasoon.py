# tests/test_module2_prasoon.py
# Unit Test Suite for Module 2: Prasoon Joshi (Patient Management / PCB)

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User
from models.patient import Patient


class TestModule2Prasoon(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        Patient.query.filter(Patient.patientName.like('Test Prasoon%')).delete()
        admin = User.query.filter_by(username="patient_admin").first()
        if not admin:
            admin = User(username="patient_admin", user_role="Admin")
            admin.set_password("pass123")
            db.session.add(admin)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(admin.user_id)
            sess['username'] = admin.username

    def tearDown(self):
        Patient.query.filter(Patient.patientName.like('Test Prasoon%')).delete()
        admin = User.query.filter_by(username="patient_admin").first()
        if admin:
            db.session.delete(admin)
        db.session.commit()
        self.ctx.pop()

    def test_01_patient_directory_renders(self):
        res = self.client.get('/patients/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Patient Management & PCB Lifecycle", res.data)

    def test_02_register_patient_process_creation(self):
        res = self.client.post('/patients/add', data={
            'patientName': 'Test Prasoon Alpha',
            'patientStatus': 'Waiting'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"registered successfully", res.data)

        p = Patient.query.filter_by(patientName='Test Prasoon Alpha').first()
        self.assertIsNotNone(p)
        self.assertEqual(p.patientStatus, 'Waiting')

    def test_03_edit_patient_state_transition(self):
        p = Patient(patientName='Test Prasoon Beta', patientStatus='Waiting')
        db.session.add(p)
        db.session.commit()

        res = self.client.post(f'/patients/edit/{p.patient_id}', data={
            'patientName': 'Test Prasoon Beta Updated',
            'patientStatus': 'Admitted'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        db.session.refresh(p)
        self.assertEqual(p.patientName, 'Test Prasoon Beta Updated')
        self.assertEqual(p.patientStatus, 'Admitted')

    def test_04_delete_patient_process_termination(self):
        p = Patient(patientName='Test Prasoon Gamma', patientStatus='Waiting')
        db.session.add(p)
        db.session.commit()

        res = self.client.get(f'/patients/delete/{p.patient_id}', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"deleted successfully", res.data)
        self.assertIsNone(Patient.query.filter_by(patientName='Test Prasoon Gamma').first())


if __name__ == '__main__':
    unittest.main()
