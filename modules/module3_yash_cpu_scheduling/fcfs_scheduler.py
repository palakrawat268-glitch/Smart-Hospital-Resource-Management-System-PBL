# modules/module3_yash_cpu_scheduling/fcfs_scheduler.py
# Author: Yash Yadav
# OS Concept: First-Come, First-Served (FCFS) CPU Scheduling

class FCFSScheduler:
    def __init__(self, doctors):
        self.doctors = doctors

    def schedule(self):
        sortedDoctors = sorted(
            self.doctors,
            key=lambda doctor: doctor.doctor_id
        )

        queuePosition = 1
        for doctor in sortedDoctors:
            doctor.queuePosition = queuePosition
            queuePosition += 1

        return sortedDoctors
