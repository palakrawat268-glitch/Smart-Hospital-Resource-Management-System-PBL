# modules/module5_kanishk_bankers/__init__.py
# Author: Kanishk Ramola
# OS Concept: Banker's Algorithm (Deadlock Avoidance) & Mutex Synchronization

from .models import Equipment, EquipmentAllocation, PatientResourceClaim
from .routes import equipment_bp
from .os_core.bankers_algorithm import BankersAlgorithm
from .os_core.deadlock_detector import DeadlockDetector
from .os_core.synchronization import equipment_sync

__all__ = [
    'Equipment',
    'EquipmentAllocation',
    'PatientResourceClaim',
    'equipment_bp',
    'BankersAlgorithm',
    'DeadlockDetector',
    'equipment_sync'
]
