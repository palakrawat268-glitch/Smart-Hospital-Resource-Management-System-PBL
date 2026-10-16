# modules/module4_sujal_memory_mgmt/models.py
# Author: Sujal Kumar
# OS Concept: Memory Management / Dynamic Partitioning (Wards = Partitions, Beds = Frames)

from extensions import db


class Ward(db.Model):
    __tablename__ = 'wards'

    ward_id = db.Column(db.Integer, primary_key=True)
    wardName = db.Column(db.String(100), unique=True, nullable=False)
    wardType = db.Column(db.String(50), nullable=False)
    wardCapacity = db.Column(db.Integer, nullable=False, default=10)
    occupiedBeds = db.Column(db.Integer, default=0)
    availableBeds = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.ward_id

    def __repr__(self):
        return f"<Ward {self.wardName} [{self.wardType}] Capacity: {self.wardCapacity}>"


class Bed(db.Model):
    __tablename__ = 'beds'

    bed_id = db.Column(db.Integer, primary_key=True)
    bedNumber = db.Column(db.String(50), unique=True, nullable=False)
    bedType = db.Column(db.String(50), nullable=False)
    bedStatus = db.Column(db.String(30), default='Available')  # Available, Occupied, Reserved, Maintenance
    bedAvailability = db.Column(db.Boolean, default=True)
    assignedPatient = db.Column(db.String(100), nullable=True)
    assignedWard = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.bed_id

    def __repr__(self):
        return f"<Bed {self.bedNumber} ({self.assignedWard}) - Status: {self.bedStatus}>"
