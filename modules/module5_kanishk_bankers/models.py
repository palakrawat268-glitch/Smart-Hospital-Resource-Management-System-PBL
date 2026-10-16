# modules/module5_kanishk_bankers/models.py
# Author: Kanishk Ramola
# OS Concept: Banker's Algorithm (Deadlock Avoidance) & Mutex Synchronization

from extensions import db


class Equipment(db.Model):
    __tablename__ = 'equipment'

    equipmentId = db.Column(db.Integer, primary_key=True)
    equipmentName = db.Column(db.String(100), nullable=False)
    equipmentType = db.Column(db.String(100), nullable=False)
    equipmentStatus = db.Column(db.Enum('Available', 'In Use', 'Maintenance', 'Unavailable'), default='Available')
    equipmentAvailability = db.Column(db.Integer, default=1)
    equipmentLocation = db.Column(db.String(100), nullable=False)
    maintenanceDate = db.Column(db.Date, nullable=True)
    createdAt = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.equipmentId

    def __repr__(self):
        return f"<Equipment {self.equipmentName} ({self.equipmentType}) - Status: {self.equipmentStatus}>"


class EquipmentAllocation(db.Model):
    __tablename__ = 'equipment_allocation'

    allocationId = db.Column(db.Integer, primary_key=True)
    equipmentId = db.Column(db.Integer, db.ForeignKey('equipment.equipmentId', ondelete='CASCADE'), nullable=False)
    patientId = db.Column(db.String(50), nullable=False)
    allocatedResources = db.Column(db.Integer, default=0)
    requestedResources = db.Column(db.Integer, default=0)
    resourceStatus = db.Column(db.Enum('Allocated', 'Waiting', 'Released', 'Denied'), default='Allocated')
    allocatedAt = db.Column(db.DateTime, server_default=db.func.now())
    releasedAt = db.Column(db.DateTime, nullable=True)

    equipment = db.relationship('Equipment', backref=db.backref('allocations', lazy=True, cascade='all, delete'))

    @property
    def id(self):
        return self.allocationId

    def __repr__(self):
        return f"<Allocation {self.allocationId} - Patient: {self.patientId} - Status: {self.resourceStatus}>"


class PatientResourceClaim(db.Model):
    __tablename__ = 'patient_resource_claim'

    claimId = db.Column(db.Integer, primary_key=True)
    patientId = db.Column(db.String(50), nullable=False)
    equipmentId = db.Column(db.Integer, db.ForeignKey('equipment.equipmentId', ondelete='CASCADE'), nullable=False)
    maximumNeed = db.Column(db.Integer, nullable=False)
    allocatedNeed = db.Column(db.Integer, default=0)
    remainingNeed = db.Column(db.Integer)

    equipment = db.relationship('Equipment', backref=db.backref('claims', lazy=True, cascade='all, delete'))

    @property
    def id(self):
        return self.claimId

    def __repr__(self):
        return f"<Claim {self.claimId} - Patient: {self.patientId} - Max: {self.maximumNeed}>"
