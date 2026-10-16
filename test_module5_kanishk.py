# tests/test_module5_kanishk.py
# Unit Test Suite for Module 5: Kanishk Ramola (Equipment Management & Banker's Algorithm)

import sys
import os
import unittest
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.user import User
from models.equipment import Equipment, EquipmentAllocation, PatientResourceClaim
from modules.module5_kanishk_bankers.os_core.bankers_algorithm import BankersAlgorithm
from modules.module5_kanishk_bankers.os_core.deadlock_detector import DeadlockDetector
from modules.module5_kanishk_bankers.os_core.synchronization import ResourceSynchronization


class TestModule5Kanishk(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        admin = User.query.filter_by(username="eq_admin").first()
        if not admin:
            admin = User(username="eq_admin", user_role="Admin")
            admin.set_password("pass123")
            db.session.add(admin)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(admin.user_id)
            sess['username'] = admin.username

    def tearDown(self):
        admin = User.query.filter_by(username="eq_admin").first()
        if admin:
            db.session.delete(admin)
        db.session.commit()
        self.ctx.pop()

    def test_01_inventory_page_renders(self):
        res = self.client.get('/inventory')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Medical Equipment Inventory", res.data)

    def test_02_allocation_page_renders(self):
        res = self.client.get('/allocation')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Banker's Algorithm", res.data)

    def test_03_bankers_algorithm_safe_state(self):
        avail = [3, 3, 2]
        max_need = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3]
        ]
        allocated = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2]
        ]
        banker = BankersAlgorithm(avail, max_need, allocated)
        is_safe, seq, logs = banker.is_safe_state()
        self.assertTrue(is_safe)
        self.assertEqual(len(seq), 5)

    def test_04_bankers_request_exceeds_need_rejected(self):
        avail = [3, 3, 2]
        max_need = [[2, 2, 2]]
        allocated = [[1, 0, 0]]
        banker = BankersAlgorithm(avail, max_need, allocated)
        # remaining need is [1, 2, 2]. Requesting 5 exceeds max claim!
        granted, msg, seq = banker.request_resources(0, [5, 0, 0])
        self.assertFalse(granted)
        self.assertIn("exceeds maximum claim", msg)

    def test_05_bankers_request_exceeds_available_rejected(self):
        avail = [1, 0, 0]
        max_need = [[5, 5, 5]]
        allocated = [[0, 0, 0]]
        banker = BankersAlgorithm(avail, max_need, allocated)
        granted, msg, seq = banker.request_resources(0, [2, 0, 0])
        self.assertFalse(granted)
        self.assertIn("unavailable", msg)

    def test_06_deadlock_detection_detects_smooth_state(self):
        avail = [0, 0, 0]
        alloc = [[1, 0], [0, 1]]
        req = [[0, 0], [0, 0]]
        detector = DeadlockDetector(2, 2, avail, alloc, req)
        has_deadlock, blocked, status = detector.detect_deadlock()
        self.assertFalse(has_deadlock)
        self.assertEqual(len(blocked), 0)

    def test_07_mutex_synchronization(self):
        sync = ResourceSynchronization()
        counter = [0]

        def worker():
            with sync.criticalSection():
                val = counter[0]
                val += 1
                counter[0] = val

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(counter[0], 10)

    def test_08_api_equipment_endpoint(self):
        res = self.client.get('/api/equipment')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)


if __name__ == '__main__':
    unittest.main()
