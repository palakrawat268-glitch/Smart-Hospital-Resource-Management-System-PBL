# tests/test_module6_himesh.py
# Unit Test Suite for Module 6: Himesh Kathait (Reports & Resource Monitoring & Deadlock Logs)

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User
from models.deadlock_log import DeadlockLog
from models.appointment import Appointment


class TestModule6Himesh(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        admin = User.query.filter_by(username="report_admin").first()
        if not admin:
            admin = User(username="report_admin", user_role="Admin")
            admin.set_password("pass123")
            db.session.add(admin)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(admin.user_id)
            sess['username'] = admin.username

    def tearDown(self):
        admin = User.query.filter_by(username="report_admin").first()
        if admin:
            db.session.delete(admin)
        db.session.commit()
        self.ctx.pop()

    def test_01_reports_dashboard_renders(self):
        """Verify report dashboard loads with stats cards and appointment breakdown"""
        res = self.client.get('/reports/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Reports & Resource Monitoring Dashboard", res.data)
        self.assertIn(b"Appointment Summary", res.data)

    def test_02_resource_monitor_renders_all_tabs(self):
        """Verify previously-missing resource_monitor.html renders beds, equipment, and wards"""
        res = self.client.get('/reports/resources')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Unified Resource Monitor", res.data)
        self.assertIn(b"Beds", res.data)
        self.assertIn(b"Medical Equipment", res.data)
        self.assertIn(b"Hospital Wards", res.data)

    def test_03_generate_report_all(self):
        """Verify generating complete hospital report renders summary metrics"""
        res = self.client.post('/reports/generate', data={'reportType': 'all'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Complete Hospital Summary Report", res.data)

    def test_04_generate_report_patients(self):
        """Verify generating patient report renders without Jinja syntax error"""
        res = self.client.post('/reports/generate', data={'reportType': 'patients'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Patient Report", res.data)

    def test_05_generate_report_doctors(self):
        """Verify generating doctor report renders priority and department columns"""
        res = self.client.post('/reports/generate', data={'reportType': 'doctors'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Doctor Report", res.data)

    def test_06_generate_report_deadlock(self):
        """Verify generating deadlock audit report renders audit records"""
        res = self.client.post('/reports/generate', data={'reportType': 'deadlock'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Deadlock Log Report", res.data)

    def test_07_export_csv_equipment(self):
        """Verify equipment CSV export returns valid text/csv attachment"""
        res = self.client.get('/reports/export/csv?type=equipment')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res.headers.get('Content-Type'))
        self.assertIn(b"Equipment Name", res.data)

    def test_08_export_csv_beds_safely_resolves_attributes(self):
        """Verify bed CSV export handles bed_id without crashing on .id"""
        res = self.client.get('/reports/export/csv?type=beds')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res.headers.get('Content-Type'))
        self.assertIn(b"Bed Number", res.data)

    def test_09_export_csv_deadlock_logs(self):
        """Verify deadlock CSV export handles log_id and timestamp correctly"""
        res = self.client.get('/reports/export/csv?type=deadlock')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/csv', res.headers.get('Content-Type'))
        self.assertIn(b"Resource Graph", res.data)

    def test_10_deadlock_view_renders_audit_history(self):
        """Verify deadlock.html is no longer 0 bytes and renders audit table"""
        res = self.client.get('/reports/deadlock')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"OS Deadlock Detection & Audit Logs", res.data)
        self.assertIn(b"Deadlock Detection Execution Log History", res.data)

    def test_11_bankers_view_renders_allocations(self):
        """Verify Banker's read-only state view loads registry table"""
        res = self.client.get('/reports/bankers')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Banker's Algorithm Resource Allocation State", res.data)

    def test_12_api_stats_json_endpoint(self):
        """Verify JSON API provides complete metrics breakdown for frontend charts"""
        res = self.client.get('/reports/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('stats', data)
        self.assertIn('appointmentStatus', data)
        self.assertIn('bedStatus', data)
        self.assertIn('equipmentStatus', data)


if __name__ == '__main__':
    unittest.main()
