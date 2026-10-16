# master_hospital_system/database/seed_data.py
# Seeds comprehensive sample data for all 6 team modules into hospital_db

import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import (
    User,
    Patient,
    Doctor,
    Ward,
    Bed,
    Equipment,
    EquipmentAllocation,
    PatientResourceClaim,
    DeadlockLog,
    Appointment
)


def seed_all():
    with app.app_context():
        print("[*] Creating all tables in MySQL 'hospital_db'...")
        db.create_all()

        # 1. Palak Rawat: Users
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", user_role="Admin", login_status="Logged Out")
            admin.set_password("admin123")
            db.session.add(admin)

        if not User.query.filter_by(username="dr_sharma").first():
            doc_user = User(username="dr_sharma", user_role="Doctor", login_status="Logged Out")
            doc_user.set_password("doctor123")
            db.session.add(doc_user)

        # 2. Yash Yadav: Doctors
        doctors_data = [
            ("Dr. Rajesh Sharma", "sharma@hospital.com", "9876543210", "Cardiology", "Chief Cardiologist", 14, "Available", "Active", "Emergency", 1),
            ("Dr. Priya Mehta", "mehta@hospital.com", "9876543211", "Neurology", "Neurosurgeon", 11, "Available", "Active", "High", 2),
            ("Dr. Amit Verma", "verma@hospital.com", "9876543212", "Emergency", "ER Specialist", 8, "Available", "Active", "Emergency", 1),
            ("Dr. Sneha Patel", "patel@hospital.com", "9876543213", "General Medicine", "General Physician", 6, "Available", "Active", "Medium", 3),
            ("Dr. Vikram Singh", "singh@hospital.com", "9876543214", "Pediatrics", "Senior Pediatrician", 9, "Available", "Active", "Low", 4),
        ]
        for name, email, phone, dept, spec, exp, avail, status, priority, q_pos in doctors_data:
            if not Doctor.query.filter_by(doctorEmail=email).first():
                doc = Doctor(
                    doctorName=name,
                    doctorEmail=email,
                    doctorPhone=phone,
                    doctorDepartment=dept,
                    doctorSpecialization=spec,
                    doctorExperience=exp,
                    doctorAvailability=avail,
                    doctorStatus=status,
                    priorityLevel=priority,
                    emergencyPriority=1 if priority == "Emergency" else 2 if priority == "High" else 3 if priority == "Medium" else 4,
                    queuePosition=q_pos
                )
                db.session.add(doc)

        # 3. Sujal Kumar: Wards & Beds
        wards_data = [
            ("ICU Ward Alpha", "ICU", 6, 2, 4),
            ("General Ward 1", "General", 10, 3, 7),
            ("Emergency Ward", "Emergency", 5, 1, 4),
            ("Pediatric Ward", "Pediatric", 8, 0, 8),
        ]
        for w_name, w_type, cap, occ, free in wards_data:
            if not Ward.query.filter_by(wardName=w_name).first():
                w = Ward(wardName=w_name, wardType=w_type, wardCapacity=cap, occupiedBeds=occ, availableBeds=free)
                db.session.add(w)

        beds_data = [
            ("ICU-01", "ICU", "Occupied", False, "Rohan Verma", "ICU Ward Alpha"),
            ("ICU-02", "ICU", "Occupied", False, "Kavita Rao", "ICU Ward Alpha"),
            ("ICU-03", "ICU", "Available", True, None, "ICU Ward Alpha"),
            ("ICU-04", "ICU", "Available", True, None, "ICU Ward Alpha"),
            ("GEN-101", "General", "Occupied", False, "Manoj Kumar", "General Ward 1"),
            ("GEN-102", "General", "Occupied", False, "Sunita Devi", "General Ward 1"),
            ("GEN-103", "General", "Occupied", False, "Deepak Joshi", "General Ward 1"),
            ("GEN-104", "General", "Available", True, None, "General Ward 1"),
            ("GEN-105", "General", "Available", True, None, "General Ward 1"),
            ("GEN-106", "General", "Maintenance", False, None, "General Ward 1"),
            ("EMG-01", "Emergency", "Occupied", False, "Ananya Sen", "Emergency Ward"),
            ("EMG-02", "Emergency", "Available", True, None, "Emergency Ward"),
        ]
        for b_num, b_type, b_stat, b_avail, patient, ward in beds_data:
            if not Bed.query.filter_by(bedNumber=b_num).first():
                b = Bed(bedNumber=b_num, bedType=b_type, bedStatus=b_stat, bedAvailability=b_avail, assignedPatient=patient, assignedWard=ward)
                db.session.add(b)

        # 4. Prasoon Joshi: Patients
        patients_data = [
            ("Rohan Verma", "Admitted", "ICU Ward Alpha", "ICU-01"),
            ("Kavita Rao", "Admitted", "ICU Ward Alpha", "ICU-02"),
            ("Manoj Kumar", "Admitted", "General Ward 1", "GEN-101"),
            ("Sunita Devi", "Admitted", "General Ward 1", "GEN-102"),
            ("Deepak Joshi", "Admitted", "General Ward 1", "GEN-103"),
            ("Ananya Sen", "Admitted", "Emergency Ward", "EMG-01"),
            ("Vikram Malhotra", "Waiting", None, None),
            ("Pooja Nair", "Waiting", None, None),
            ("Harish Chandra", "Discharged", None, None),
        ]
        for p_name, p_stat, w_name, b_num in patients_data:
            if not Patient.query.filter_by(patientName=p_name).first():
                p = Patient(patientName=p_name, patientStatus=p_stat, assignedWard=w_name, assignedBed=b_num)
                db.session.add(p)

        # 5. Kanishk Ramola: Equipment & Banker's Claims
        equipment_data = [
            ("Ventilator-A", "Life Support", "Available", 3, "ICU Ward 1", date(2026, 11, 15)),
            ("Patient Monitor-B", "Monitoring", "Available", 5, "ICU Ward 2", date(2026, 12, 1)),
            ("Defibrillator-C", "Emergency Resuscitation", "Available", 2, "Emergency OT", date(2026, 11, 30)),
            ("Dialysis Machine-D", "Nephrology", "Available", 2, "Dialysis Unit", date(2026, 12, 20)),
            ("Oxygen Concentrator-E", "Respiratory Support", "Available", 4, "General Ward 3", date(2026, 11, 25)),
        ]
        for eq_name, eq_type, eq_stat, eq_avail, loc, m_date in equipment_data:
            if not Equipment.query.filter_by(equipmentName=eq_name).first():
                eq = Equipment(
                    equipmentName=eq_name,
                    equipmentType=eq_type,
                    equipmentStatus=eq_stat,
                    equipmentAvailability=eq_avail,
                    equipmentLocation=loc,
                    maintenanceDate=m_date
                )
                db.session.add(eq)

        # Commit initial equipment to obtain IDs
        db.session.commit()

        # Seed Claims for Banker's Algorithm
        if not PatientResourceClaim.query.first():
            claims_seed = [
                ("Patient_P0", 1, 2, 1),
                ("Patient_P0", 2, 3, 1),
                ("Patient_P0", 3, 1, 0),
                ("Patient_P1", 1, 3, 1),
                ("Patient_P1", 2, 2, 2),
                ("Patient_P1", 3, 2, 0),
                ("Patient_P2", 1, 2, 0),
                ("Patient_P2", 2, 2, 0),
                ("Patient_P2", 3, 1, 1),
            ]
            for pid, eq_id, max_n, alloc_n in claims_seed:
                c = PatientResourceClaim(patientId=pid, equipmentId=eq_id, maximumNeed=max_n, allocatedNeed=alloc_n)
                db.session.add(c)

        if not EquipmentAllocation.query.first():
            allocs_seed = [
                (1, "Patient_P0", 1, 1, 'Allocated'),
                (2, "Patient_P0", 1, 1, 'Allocated'),
                (1, "Patient_P1", 1, 1, 'Allocated'),
                (2, "Patient_P1", 2, 2, 'Allocated'),
                (3, "Patient_P2", 1, 1, 'Allocated'),
            ]
            for eq_id, pid, alloc_r, req_r, stat in allocs_seed:
                a = EquipmentAllocation(equipmentId=eq_id, patientId=pid, allocatedResources=alloc_r, requestedResources=req_r, resourceStatus=stat)
                db.session.add(a)

        # 6. Himesh Kathait: Deadlock Logs & Appointments
        if not DeadlockLog.query.first():
            dl1 = DeadlockLog(
                waitingQueue="Patient_P0,Patient_P1",
                blockedProcesses="None",
                resourceGraph="{'Patient_P0': [], 'Patient_P1': [], 'Patient_P2': []}",
                deadlockStatus="No Deadlock"
            )
            db.session.add(dl1)

        if not Appointment.query.first():
            appts_seed = [
                (1, 1, date(2026, 10, 16), "10:30 AM", "Confirmed", "Routine Cardiac Checkup", "General"),
                (2, 2, date(2026, 10, 16), "11:00 AM", "Pending", "Severe Migraine Consultation", "General"),
                (3, 3, date(2026, 10, 16), "09:00 AM", "Completed", "Trauma Assessment", "Emergency"),
                (4, 4, date(2026, 10, 17), "02:00 PM", "Cancelled", "Follow-up", "Follow-up"),
            ]
            for pid, did, dt, tm, stat, rsn, tp in appts_seed:
                apt = Appointment(patient_id=pid, doctor_id=did, appointmentDate=dt, appointmentTime=tm, appointmentStatus=stat, appointmentReason=rsn, appointmentType=tp)
                db.session.add(apt)

        db.session.commit()
        print("[SUCCESS] Database seeded successfully with data for all 6 modules!")


if __name__ == '__main__':
    seed_all()
