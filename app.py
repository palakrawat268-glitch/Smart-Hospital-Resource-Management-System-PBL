# master_hospital_system/app.py
# Smart Hospital Resource Management and Reallocation System
# Master Central Flask Application integrating all 6 teammate modules

import sys
import os

# Ensure local modules can be cleanly imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, redirect, url_for
from flask_login import current_user

from config import Config
from extensions import db, bcrypt, login_manager

# Import Models
from models import (
    User,
    Patient,
    Doctor,
    Ward,
    Bed,
    Equipment,
    EquipmentAllocation,
    PatientResourceClaim,
    DeadlockLog,
    Appointment
)

# Import Blueprints from each student module
from modules.module1_palak_auth import auth_bp, dashboard_bp
from modules.module2_prasoon_patient import patient_bp
from modules.module3_yash_cpu_scheduling import doctor_bp, os_bp
from modules.module4_sujal_memory_mgmt import bed_bp
from modules.module5_kanishk_bankers import equipment_bp
from modules.module6_himesh_deadlock_reports import report_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints for all 6 modules
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(os_bp)
    app.register_blueprint(bed_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(report_bp)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.dashboard'))
        return redirect(url_for('auth.login'))

    # Context Processor: Inject Team and System Info across all templates
    @app.context_processor
    def inject_system_meta():
        return {
            'system_title': 'Smart Hospital Resource Management System',
            'team_name': 'Team Palak Rawat (2419261)',
            'modules_meta': [
                {'module': 1, 'author': 'Palak Rawat', 'name': 'Auth & Dashboard', 'algo': 'Process Sync / Session Control'},
                {'module': 2, 'author': 'Prasoon Joshi', 'name': 'Patient Management', 'algo': 'Process PCB Lifecycle'},
                {'module': 3, 'author': 'Yash Yadav', 'name': 'Doctor Management', 'algo': 'CPU Scheduling (FCFS & Priority)'},
                {'module': 4, 'author': 'Sujal Kumar', 'name': 'Bed & Ward Management', 'algo': 'Dynamic Partitioning'},
                {'module': 5, 'author': 'Kanishk Ramola', 'name': 'Equipment Management', 'algo': 'Banker\'s Algorithm & Mutex'},
                {'module': 6, 'author': 'Himesh Kathait', 'name': 'Reports & Resource Monitoring', 'algo': 'Deadlock Detection & RAG'}
            ]
        }

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
