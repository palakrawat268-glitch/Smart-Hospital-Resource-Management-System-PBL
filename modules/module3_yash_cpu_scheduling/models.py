# modules/module3_yash_cpu_scheduling/models.py
# Author: Yash Yadav
# OS Concept: CPU Scheduling (FCFS & Non-Preemptive Priority Scheduling)

from extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    doctor_id = db.Column(db.Integer, primary_key=True)
    doctorName = db.Column(db.String(100), nullable=False)
    doctorEmail = db.Column(db.String(100), unique=True, nullable=False)
    doctorPhone = db.Column(db.String(15), nullable=False)
    doctorDepartment = db.Column(db.String(100), nullable=False)
    doctorSpecialization = db.Column(db.String(100), nullable=False)
    doctorExperience = db.Column(db.Integer, nullable=False)
    doctorAvailability = db.Column(db.String(20), default="Available")
    doctorStatus = db.Column(db.String(20), default="Active")
    priorityLevel = db.Column(db.String(20), default="Medium")
    emergencyPriority = db.Column(db.Integer, default=2)
    queuePosition = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.doctor_id

    @property
    def doctor_name(self):
        return self.doctorName

    @property
    def department(self):
        return self.doctorDepartment

    @property
    def priority_level(self):
        return self.priorityLevel

    def __repr__(self):
        return f"<Doctor {self.doctorName} ({self.doctorDepartment}) - Priority: {self.priorityLevel}>"
