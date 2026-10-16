# master_hospital_system/models/__init__.py
# Master Models Registry uniting all 6 team member modules

from extensions import db

# Module 1 (Palak Rawat)
from modules.module1_palak_auth.models import User

# Module 2 (Prasoon Joshi)
from modules.module2_prasoon_patient.models import Patient

# Module 3 (Yash Yadav)
from modules.module3_yash_cpu_scheduling.models import Doctor

# Module 4 (Sujal Kumar)
from modules.module4_sujal_memory_mgmt.models import Ward, Bed

# Module 5 (Kanishk Ramola)
from modules.module5_kanishk_bankers.models import Equipment, EquipmentAllocation, PatientResourceClaim

# Module 6 (Himesh Kathait)
from modules.module6_himesh_deadlock_reports.models import DeadlockLog, Appointment

__all__ = [
    'db',
    'User',
    'Patient',
    'Doctor',
    'Ward',
    'Bed',
    'Equipment',
    'EquipmentAllocation',
    'PatientResourceClaim',
    'DeadlockLog',
    'Appointment'
]
