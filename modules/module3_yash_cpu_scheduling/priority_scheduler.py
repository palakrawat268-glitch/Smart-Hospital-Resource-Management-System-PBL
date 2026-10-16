# modules/module3_yash_cpu_scheduling/priority_scheduler.py
# Author: Yash Yadav
# OS Concept: Non-Preemptive Priority CPU Scheduling

class PriorityScheduler:
    def __init__(self, doctors):
        self.doctors = doctors

    def get_priority_value(self, priorityLevel):
        priority_map = {
            "Emergency": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4
        }
        return priority_map.get(priorityLevel, 5)

    def schedule(self):
        sortedDoctors = sorted(
            self.doctors,
            key=lambda doctor: (
                self.get_priority_value(getattr(doctor, 'priority_level', getattr(doctor, 'priorityLevel', 'Medium'))),
                doctor.doctor_id
            )
        )

        queuePosition = 1
        for doctor in sortedDoctors:
            doctor.queuePosition = queuePosition
            lvl = getattr(doctor, 'priority_level', getattr(doctor, 'priorityLevel', 'Medium'))
            doctor.emergencyPriority = self.get_priority_value(lvl)
            queuePosition += 1

        return sortedDoctors
