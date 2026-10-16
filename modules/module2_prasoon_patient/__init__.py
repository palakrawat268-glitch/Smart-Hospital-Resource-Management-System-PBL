# modules/module2_prasoon_patient/__init__.py
# Author: Prasoon Joshi
# OS Concept: Process Control Block (PCB) / Patient Lifecycle Management

from .models import Patient
from .routes import patient_bp

__all__ = ['Patient', 'patient_bp']
