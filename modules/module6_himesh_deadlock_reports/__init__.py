# modules/module6_himesh_deadlock_reports/__init__.py
# Author: Himesh Kathait
# OS Concept: Resource Allocation Graph (RAG) & Deadlock Detection Audit Logging

from .models import DeadlockLog, Appointment
from .routes import report_bp, get_dashboard_stats

__all__ = ['DeadlockLog', 'Appointment', 'report_bp', 'get_dashboard_stats']
