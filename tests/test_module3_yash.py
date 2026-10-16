# tests/test_module3_yash.py
# Unit Test Suite for Module 3: Yash Yadav (Doctor Management & CPU Scheduling)

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User
from models.doctor import Doctor


class TestModule3Yash(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        Doctor.query.filter(Doctor.doctorEmail.like('test_yash_%')).delete()
        admin = User.query.filter_by(username="doc_admin").first()
        if not admin:
            admin = User(username="doc_admin", user_role="Admin")
            admin.set_password("pass123")
            db.session.add(admin)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(admin.user_id)
            sess['username'] = admin.username

    def tearDown(self):
        Doctor.query.filter(Doctor.doctorEmail.like('test_yash_%')).delete()
        admin = User.query.filter_by(username="doc_admin").first()
        if admin:
            db.session.delete(admin)
        db.session.commit()
        self.ctx.pop()

    def test_01_doctor_list_page_renders(self):
        res = self.client.get('/doctor/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Doctor Management & CPU Scheduling", res.data)

    def test_02_add_doctor_success(self):
        res = self.client.post('/doctor/add', data={
            'doctorName': 'Dr. Test Yash',
            'doctorEmail': 'test_yash_one@hospital.com',
            'doctorPhone': '9876543299',
            'doctorDepartment': 'Cardiology',
            'doctorSpecialization': 'Surgeon',
            'doctorExperience': '10',
            'priorityLevel': 'Emergency'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Doctor added successfully", res.data)

        d = Doctor.query.filter_by(doctorEmail='test_yash_one@hospital.com').first()
        self.assertIsNotNone(d)
        self.assertEqual(d.priorityLevel, 'Emergency')
        self.assertEqual(d.emergencyPriority, 1)

    def test_03_edit_doctor_success(self):
        d = Doctor(
            doctorName='Dr. Yash Initial',
            doctorEmail='test_yash_edit@hospital.com',
            doctorPhone='9876543298',
            doctorDepartment='General',
            doctorSpecialization='Physician',
            doctorExperience=4,
            priorityLevel='Low'
        )
        db.session.add(d)
        db.session.commit()

        res = self.client.post(f'/doctor/edit/{d.doctor_id}', data={
            'doctorName': 'Dr. Yash Updated',
            'doctorEmail': 'test_yash_edit@hospital.com',
            'doctorPhone': '9876543298',
            'doctorDepartment': 'Cardiology',
            'doctorSpecialization': 'Specialist',
            'doctorExperience': '5',
            'doctorAvailability': 'Available',
            'doctorStatus': 'Active',
            'priorityLevel': 'High'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        db.session.refresh(d)
        self.assertEqual(d.doctorName, 'Dr. Yash Updated')
        self.assertEqual(d.priorityLevel, 'High')
        self.assertEqual(d.emergencyPriority, 2)

    def test_04_fcfs_scheduling_sets_queue_positions(self):
        d1 = Doctor(doctorName='Dr. Yash FCFS1', doctorEmail='test_yash_fcfs1@hospital.com', doctorPhone='111', doctorDepartment='A', doctorSpecialization='A', doctorExperience=1, doctorStatus='Active')
        d2 = Doctor(doctorName='Dr. Yash FCFS2', doctorEmail='test_yash_fcfs2@hospital.com', doctorPhone='222', doctorDepartment='B', doctorSpecialization='B', doctorExperience=2, doctorStatus='Active')
        db.session.add_all([d1, d2])
        db.session.commit()

        res = self.client.get('/os/fcfs', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"FCFS CPU Scheduling Applied Successfully", res.data)

        db.session.refresh(d1)
        db.session.refresh(d2)
        self.assertTrue(d1.queuePosition > 0)
        self.assertTrue(d2.queuePosition > 0)

    def test_05_priority_scheduling_places_emergency_first(self):
        d_low = Doctor(doctorName='Dr. Low Pri', doctorEmail='test_yash_low@hospital.com', doctorPhone='111', doctorDepartment='A', doctorSpecialization='A', doctorExperience=1, priorityLevel='Low', doctorStatus='Active')
        d_emg = Doctor(doctorName='Dr. Emg Pri', doctorEmail='test_yash_emg@hospital.com', doctorPhone='222', doctorDepartment='B', doctorSpecialization='B', doctorExperience=2, priorityLevel='Emergency', doctorStatus='Active')
        db.session.add_all([d_low, d_emg])
        db.session.commit()

        res = self.client.get('/os/priority', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Priority CPU Scheduling Applied Successfully", res.data)

        db.session.refresh(d_emg)
        db.session.refresh(d_low)
        self.assertTrue(d_emg.queuePosition < d_low.queuePosition)


if __name__ == '__main__':
    unittest.main()
