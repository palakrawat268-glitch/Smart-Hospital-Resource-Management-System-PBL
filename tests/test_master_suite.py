# tests/test_master_suite.py
# Master Integration Verification Test Runner
# Runs all 6 teammate modules and displays unified scorecard

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_module1_palak import TestModule1Palak
from tests.test_module2_prasoon import TestModule2Prasoon
from tests.test_module3_yash import TestModule3Yash
from tests.test_module4_sujal import TestModule4Sujal
from tests.test_module5_kanishk import TestModule5Kanishk
from tests.test_module6_himesh import TestModule6Himesh


def run_master_test_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    modules_to_test = [
        ("Module 1: Palak Rawat", "User Auth & Session Control", "Process Synchronization", TestModule1Palak),
        ("Module 2: Prasoon Joshi", "Patient Management", "Process Control Block (PCB)", TestModule2Prasoon),
        ("Module 3: Yash Yadav", "Doctor Management", "CPU Scheduling (FCFS & Priority)", TestModule3Yash),
        ("Module 4: Sujal Kumar", "Bed & Ward Management", "Dynamic Partitioning", TestModule4Sujal),
        ("Module 5: Kanishk Ramola", "Equipment Management", "Banker's Algorithm & Mutex", TestModule5Kanishk),
        ("Module 6: Himesh Kathait", "Reports & Monitoring", "Deadlock Detection & RAG Logs", TestModule6Himesh),
    ]

    print("=" * 85)
    print("   [+] SMART HOSPITAL RESOURCE MANAGEMENT AND REALLOCATION SYSTEM")
    print("   MASTER INTEGRATION VERIFICATION TEST SUITE")
    print("=" * 85)

    results_table = []
    all_passed = True

    for mod_name, domain, algo, test_cls in modules_to_test:
        mod_suite = loader.loadTestsFromTestCase(test_cls)
        runner = unittest.TextTestRunner(verbosity=0)
        res = runner.run(mod_suite)

        passed = res.testsRun - len(res.failures) - len(res.errors)
        status = "PASSED" if res.wasSuccessful() else "FAILED"
        if not res.wasSuccessful():
            all_passed = False

        results_table.append({
            "module": mod_name,
            "domain": domain,
            "algo": algo,
            "total": res.testsRun,
            "passed": passed,
            "status": status
        })

    print(f"\n{'MODULE':<26} | {'DOMAIN':<22} | {'OS ALGORITHM':<30} | {'TESTS':<7} | {'STATUS'}")
    print("-" * 105)
    total_tests = 0
    total_passed = 0
    for r in results_table:
        print(f"{r['module']:<26} | {r['domain']:<22} | {r['algo']:<30} | {r['passed']}/{r['total']:<5} | {r['status']}")
        total_tests += r['total']
        total_passed += r['passed']
    print("-" * 105)
    print(f"{'OVERALL TOTALS':<83} | {total_passed}/{total_tests:<5} | {'SUCCESS' if all_passed else 'FAILURE'}")
    print("=" * 105)

    return all_passed


if __name__ == '__main__':
    success = run_master_test_suite()
    sys.exit(0 if success else 1)
