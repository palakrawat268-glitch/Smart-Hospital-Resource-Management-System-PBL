# master_hospital_system/run.py
# Single-entrypoint launcher for the Smart Hospital Master System

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("=" * 75)
    print("   [+] SMART HOSPITAL RESOURCE MANAGEMENT AND REALLOCATION SYSTEM")
    print("   Master Integration (All 6 Modules + OS Algorithms)")
    print("   Running on: http://127.0.0.1:5000")
    print("=" * 75)
    app.run(host='0.0.0.0', port=5000, debug=True)
