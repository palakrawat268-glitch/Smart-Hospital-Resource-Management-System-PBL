# modules/module6_himesh_deadlock_reports/models.py
# Author: Himesh Kathait
# OS Concept: Resource Allocation Graph (RAG) & Deadlock Detection Audit Logging

from extensions import db


class DeadlockLog(db.Model):
    __tablename__ = 'deadlock_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    waitingQueue = db.Column(db.Text, nullable=True)
    blockedProcesses = db.Column(db.Text, nullable=True)
    resourceGraph = db.Column(db.Text, nullable=True)
    deadlockStatus = db.Column(db.String(50), default='No Deadlock')
    detectedAt = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.log_id

    def __repr__(self):
        return f"<DeadlockLog {self.log_id} - Status: {self.deadlockStatus} at {self.detectedAt}>"


class Appointment(db.Model):
    __tablename__ = 'appointments'

    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=True)
    doctor_id = db.Column(db.Integer, nullable=True)
    appointmentDate = db.Column(db.Date, nullable=True)
    appointmentTime = db.Column(db.String(20), nullable=True)
    appointmentStatus = db.Column(db.String(30), default='Confirmed')  # Pending, Confirmed, Completed, Cancelled
    appointmentReason = db.Column(db.String(255), nullable=True)
    appointmentType = db.Column(db.String(50), default='General')  # Emergency, General, Follow-up
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.appointment_id

    def __repr__(self):
        return f"<Appointment {self.appointment_id} - Status: {self.appointmentStatus} - Type: {self.appointmentType}>"
