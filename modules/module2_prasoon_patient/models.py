# modules/module2_prasoon_patient/models.py
# Author: Prasoon Joshi
# OS Concept: Process Control Block (PCB) / Patient Process Lifecycle

from extensions import db


class Patient(db.Model):
    __tablename__ = 'patients'

    patient_id = db.Column(db.Integer, primary_key=True)
    patientName = db.Column(db.String(100), nullable=False)
    patientStatus = db.Column(db.String(50), default='Waiting')  # Waiting, Admitted, Discharged
    assignedWard = db.Column(db.String(100), nullable=True)
    assignedBed = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.patient_id

    def __repr__(self):
        return f"<Patient {self.patientName} [{self.patientStatus}]>"
