# modules/module3_yash_cpu_scheduling/__init__.py
# Author: Yash Yadav
# OS Concept: CPU Scheduling (FCFS & Non-Preemptive Priority)

from .models import Doctor
from .fcfs_scheduler import FCFSScheduler
from .priority_scheduler import PriorityScheduler
from .routes import doctor_bp, os_bp

__all__ = ['Doctor', 'FCFSScheduler', 'PriorityScheduler', 'doctor_bp', 'os_bp']
