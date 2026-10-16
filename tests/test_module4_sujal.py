# tests/test_module4_sujal.py
# Unit Test Suite for Module 4: Sujal Kumar (Bed & Ward Dynamic Partitioning)

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User
from models.ward import Ward
from models.bed import Bed
from models.patient import Patient


class TestModule4Sujal(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        Bed.query.filter(Bed.bedNumber.like('TEST-M4-%')).delete()
        Ward.query.filter(Ward.wardName.like('Test Ward M4%')).delete()
        Patient.query.filter(Patient.patientName.like('Test Patient M4%')).delete()

        admin = User.query.filter_by(username="bed_admin").first()
        if not admin:
            admin = User(username="bed_admin", user_role="Admin")
            admin.set_password("pass123")
            db.session.add(admin)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(admin.user_id)
            sess['username'] = admin.username

    def tearDown(self):
        Bed.query.filter(Bed.bedNumber.like('TEST-M4-%')).delete()
        Ward.query.filter(Ward.wardName.like('Test Ward M4%')).delete()
        Patient.query.filter(Patient.patientName.like('Test Patient M4%')).delete()
        admin = User.query.filter_by(username="bed_admin").first()
        if admin:
            db.session.delete(admin)
        db.session.commit()
        self.ctx.pop()

    def test_01_bed_dashboard_renders(self):
        res = self.client.get('/beds/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Bed & Ward Overview", res.data)

    def test_02_add_ward_success(self):
        res = self.client.post('/beds/wards/add', data={
            'wardName': 'Test Ward M4 Alpha',
            'wardType': 'ICU',
            'wardCapacity': '12'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"added successfully", res.data)

    def test_03_duplicate_ward_rejected(self):
        self.client.post('/beds/wards/add', data={'wardName': 'Test Ward M4 Alpha', 'wardType': 'ICU', 'wardCapacity': '10'})
        res = self.client.post('/beds/wards/add', data={'wardName': 'Test Ward M4 Alpha', 'wardType': 'General', 'wardCapacity': '15'}, follow_redirects=True)
        self.assertIn(b"already exists", res.data)

    def test_04_edit_ward_success(self):
        w = Ward(wardName='Test Ward M4 Beta', wardType='General', wardCapacity=10, occupiedBeds=1, availableBeds=9)
        db.session.add(w)
        db.session.commit()

        res = self.client.post(f'/beds/wards/edit/{w.ward_id}', data={
            'wardName': 'Test Ward M4 Beta Renamed',
            'wardType': 'ICU',
            'wardCapacity': '14'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        db.session.refresh(w)
        self.assertEqual(w.wardName, 'Test Ward M4 Beta Renamed')
        self.assertEqual(w.wardCapacity, 14)

    def test_05_add_bed_and_capacity_limit(self):
        w = Ward(wardName='Test Ward M4 Gamma', wardType='ICU', wardCapacity=1, occupiedBeds=0, availableBeds=1)
        db.session.add(w)
        db.session.commit()

        res1 = self.client.post('/beds/beds/add', data={
            'bedNumber': 'TEST-M4-B1',
            'bedType': 'ICU',
            'assignedWard': 'Test Ward M4 Gamma',
            'bedStatus': 'Available'
        }, follow_redirects=True)
        self.assertEqual(res1.status_code, 200)

        # Second bed exceeds capacity of 1
        res2 = self.client.post('/beds/beds/add', data={
            'bedNumber': 'TEST-M4-B2',
            'bedType': 'ICU',
            'assignedWard': 'Test Ward M4 Gamma',
            'bedStatus': 'Available'
        }, follow_redirects=True)
        self.assertIn(b"at full capacity", res2.data)

    def test_06_assign_bed_success(self):
        w = Ward(wardName='Test Ward M4 Delta', wardType='General', wardCapacity=5, occupiedBeds=0, availableBeds=5)
        b = Bed(bedNumber='TEST-M4-B10', bedType='General', bedStatus='Available', bedAvailability=True, assignedWard='Test Ward M4 Delta')
        db.session.add_all([w, b])
        db.session.commit()

        res = self.client.post(f'/beds/beds/assign/{b.bed_id}', data={
            'assignedPatient': 'Test Patient M4 John'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        db.session.refresh(b)
        self.assertEqual(b.bedStatus, 'Occupied')
        self.assertEqual(b.assignedPatient, 'Test Patient M4 John')

    def test_07_discharge_bed_success(self):
        w = Ward(wardName='Test Ward M4 Delta', wardType='General', wardCapacity=5, occupiedBeds=1, availableBeds=4)
        b = Bed(bedNumber='TEST-M4-B11', bedType='General', bedStatus='Occupied', bedAvailability=False, assignedPatient='Test Patient M4 Jane', assignedWard='Test Ward M4 Delta')
        db.session.add_all([w, b])
        db.session.commit()

        res = self.client.get(f'/beds/beds/discharge/{b.bed_id}', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        db.session.refresh(b)
        self.assertEqual(b.bedStatus, 'Available')
        self.assertIsNone(b.assignedPatient)

    def test_08_transfer_bed_success(self):
        w1 = Ward(wardName='Test Ward M4 W1', wardType='General', wardCapacity=5, occupiedBeds=1, availableBeds=4)
        w2 = Ward(wardName='Test Ward M4 W2', wardType='ICU', wardCapacity=5, occupiedBeds=0, availableBeds=5)
        b1 = Bed(bedNumber='TEST-M4-T1', bedType='General', bedStatus='Occupied', bedAvailability=False, assignedPatient='Test Patient M4 Mover', assignedWard='Test Ward M4 W1')
        b2 = Bed(bedNumber='TEST-M4-T2', bedType='ICU', bedStatus='Available', bedAvailability=True, assignedWard='Test Ward M4 W2')
        db.session.add_all([w1, w2, b1, b2])
        db.session.commit()

        res = self.client.post(f'/beds/beds/transfer/{b1.bed_id}', data={'toBedId': str(b2.bed_id)}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        db.session.refresh(b1)
        db.session.refresh(b2)
        self.assertEqual(b1.bedStatus, 'Available')
        self.assertEqual(b2.bedStatus, 'Occupied')
        self.assertEqual(b2.assignedPatient, 'Test Patient M4 Mover')

    def test_09_assign_bed_rejects_maintenance_bed(self):
        w = Ward(wardName='Test Ward M4 Edge', wardType='General', wardCapacity=5, occupiedBeds=0, availableBeds=4)
        b = Bed(bedNumber='TEST-M4-MNT', bedType='General', bedStatus='Maintenance', bedAvailability=False, assignedWard='Test Ward M4 Edge')
        db.session.add_all([w, b])
        db.session.commit()

        res = self.client.post(f'/beds/beds/assign/{b.bed_id}', data={'assignedPatient': 'Test Patient M4 Edge'}, follow_redirects=True)
        self.assertIn(b"is not available for assignment", res.data)

    def test_10_assign_bed_rejects_already_assigned_patient(self):
        w = Ward(wardName='Test Ward M4 Edge2', wardType='General', wardCapacity=5, occupiedBeds=1, availableBeds=4)
        b1 = Bed(bedNumber='TEST-M4-H1', bedType='General', bedStatus='Occupied', bedAvailability=False, assignedPatient='Test Patient M4 Dual', assignedWard='Test Ward M4 Edge2')
        b2 = Bed(bedNumber='TEST-M4-H2', bedType='General', bedStatus='Available', bedAvailability=True, assignedWard='Test Ward M4 Edge2')
        db.session.add_all([w, b1, b2])
        db.session.commit()

        res = self.client.post(f'/beds/beds/assign/{b2.bed_id}', data={'assignedPatient': 'Test Patient M4 Dual'}, follow_redirects=True)
        self.assertIn(b"is already assigned to Bed", res.data)

    def test_11_edit_ward_rejects_capacity_below_total_beds(self):
        w = Ward(wardName='Test Ward M4 Edge3', wardType='General', wardCapacity=5, occupiedBeds=0, availableBeds=5)
        db.session.add(w)
        db.session.commit()

        b1 = Bed(bedNumber='TEST-M4-C1', bedType='General', bedStatus='Available', bedAvailability=True, assignedWard='Test Ward M4 Edge3')
        b2 = Bed(bedNumber='TEST-M4-C2', bedType='General', bedStatus='Available', bedAvailability=True, assignedWard='Test Ward M4 Edge3')
        db.session.add_all([b1, b2])
        db.session.commit()

        res = self.client.post(f'/beds/wards/edit/{w.ward_id}', data={'wardName': 'Test Ward M4 Edge3', 'wardType': 'General', 'wardCapacity': '1'}, follow_redirects=True)
        self.assertIn(b"below total existing beds", res.data)

    def test_12_dashboard_handles_zero_capacity_ward(self):
        w = Ward(wardName='Test Ward M4 Zero', wardType='General', wardCapacity=0, occupiedBeds=0, availableBeds=0)
        db.session.add(w)
        db.session.commit()

        res = self.client.get('/beds/dashboard')
        self.assertEqual(res.status_code, 200)


if __name__ == '__main__':
    unittest.main()
