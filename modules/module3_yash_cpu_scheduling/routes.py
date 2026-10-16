# modules/module3_yash_cpu_scheduling/routes.py
# Author: Yash Yadav
# Module 3: Doctor Management & CPU Scheduling (FCFS and Priority Scheduling)

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from .models import Doctor
from .fcfs_scheduler import FCFSScheduler
from .priority_scheduler import PriorityScheduler

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")
os_bp = Blueprint("os", __name__, url_prefix="/os")

PRIORITY_MAP = {
    "Emergency": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4
}


# ============================================================================
# DOCTOR CRUD ROUTES (Yash Yadav)
# ============================================================================

@doctor_bp.route("/")
@login_required
def doctor_list():
    doctors = Doctor.query.order_by(
        db.case((Doctor.queuePosition > 0, Doctor.queuePosition), else_=9999),
        Doctor.doctor_id
    ).all()
    return render_template("doctors/doc_list.html", doctors=doctors)


@doctor_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_doctor():
    if request.method == "POST":
        doctorName = request.form.get("doctorName", "").strip()
        doctorEmail = request.form.get("doctorEmail", "").strip()
        doctorPhone = request.form.get("doctorPhone", "").strip()
        doctorDepartment = request.form.get("doctorDepartment", "").strip()
        doctorSpecialization = request.form.get("doctorSpecialization", "").strip()
        doctorExperience = request.form.get("doctorExperience", "0")
        priorityLevel = request.form.get("priorityLevel", "Medium")

        if not doctorName or not doctorEmail:
            flash("Doctor Name and Email are required.", "warning")
            return redirect(url_for("doctor.add_doctor"))

        try:
            exp = int(doctorExperience)
        except (ValueError, TypeError):
            exp = 0

        existingDoctor = Doctor.query.filter_by(doctorEmail=doctorEmail).first()
        if existingDoctor:
            flash("Doctor with this email already exists.", "danger")
            return redirect(url_for("doctor.add_doctor"))

        emergencyPriority = PRIORITY_MAP.get(priorityLevel, 3)

        newDoctor = Doctor(
            doctorName=doctorName,
            doctorEmail=doctorEmail,
            doctorPhone=doctorPhone,
            doctorDepartment=doctorDepartment,
            doctorSpecialization=doctorSpecialization,
            doctorExperience=exp,
            doctorAvailability="Available",
            doctorStatus="Active",
            priorityLevel=priorityLevel,
            emergencyPriority=emergencyPriority,
            queuePosition=0
        )

        try:
            db.session.add(newDoctor)
            db.session.commit()
            flash("Doctor added successfully.", "success")
            return redirect(url_for("doctor.doctor_list"))
        except IntegrityError:
            db.session.rollback()
            flash("Doctor with this email already exists.", "danger")
            return redirect(url_for("doctor.add_doctor"))
        except Exception:
            db.session.rollback()
            flash("An unexpected error occurred. Please try again.", "danger")
            return redirect(url_for("doctor.add_doctor"))

    return render_template("doctors/add_doctor.html")


@doctor_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_doctor(id):
    doctor = db.session.get(Doctor, id)
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctor.doctor_list"))

    if request.method == "POST":
        doctorName = request.form.get("doctorName", "").strip()
        doctorEmail = request.form.get("doctorEmail", "").strip()
        doctorPhone = request.form.get("doctorPhone", "").strip()
        doctorDepartment = request.form.get("doctorDepartment", "").strip()
        doctorSpecialization = request.form.get("doctorSpecialization", "").strip()
        doctorExperience = request.form.get("doctorExperience", "0")
        doctorAvailability = request.form.get("doctorAvailability", "Available")
        doctorStatus = request.form.get("doctorStatus", "Active")
        priorityLevel = request.form.get("priorityLevel", "Medium")

        if not doctorName or not doctorEmail:
            flash("Doctor Name and Email are required.", "warning")
            return redirect(url_for("doctor.edit_doctor", id=id))

        try:
            exp = int(doctorExperience)
        except (ValueError, TypeError):
            exp = 0

        collision = Doctor.query.filter(Doctor.doctorEmail == doctorEmail, Doctor.doctor_id != id).first()
        if collision:
            flash("Another doctor already uses this email address.", "danger")
            return redirect(url_for("doctor.edit_doctor", id=id))

        doctor.doctorName = doctorName
        doctor.doctorEmail = doctorEmail
        doctor.doctorPhone = doctorPhone
        doctor.doctorDepartment = doctorDepartment
        doctor.doctorSpecialization = doctorSpecialization
        doctor.doctorExperience = exp
        doctor.doctorAvailability = doctorAvailability
        doctor.doctorStatus = doctorStatus
        doctor.priorityLevel = priorityLevel
        doctor.emergencyPriority = PRIORITY_MAP.get(priorityLevel, 3)

        try:
            db.session.commit()
            flash("Doctor updated successfully.", "success")
            return redirect(url_for("doctor.doctor_list"))
        except IntegrityError:
            db.session.rollback()
            flash("Another doctor already uses this email address.", "danger")
            return redirect(url_for("doctor.edit_doctor", id=id))
        except Exception:
            db.session.rollback()
            flash("Failed to update doctor. Please try again.", "danger")
            return redirect(url_for("doctor.edit_doctor", id=id))

    return render_template("doctors/edit_doc.html", doctor=doctor)


@doctor_bp.route("/delete/<int:id>")
@login_required
def delete_doctor(id):
    doctor = db.session.get(Doctor, id)
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctor.doctor_list"))

    try:
        db.session.delete(doctor)
        db.session.commit()
        flash("Doctor deleted successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to delete doctor.", "danger")

    return redirect(url_for("doctor.doctor_list"))


# ============================================================================
# OS CPU SCHEDULING ROUTES (FCFS & PRIORITY)
# ============================================================================

@os_bp.route("/fcfs")
@login_required
def run_fcfs():
    try:
        active_doctors = Doctor.query.filter_by(doctorStatus="Active").all()
        scheduler = FCFSScheduler(active_doctors)
        scheduled = scheduler.schedule()
        Doctor.query.filter(Doctor.doctorStatus != "Active").update({"queuePosition": 0})
        db.session.commit()
        flash("FCFS CPU Scheduling Applied Successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to apply FCFS scheduling.", "danger")

    return redirect(url_for("doctor.doctor_list"))


@os_bp.route("/priority")
@login_required
def run_priority():
    try:
        active_doctors = Doctor.query.filter_by(doctorStatus="Active").all()
        scheduler = PriorityScheduler(active_doctors)
        scheduled = scheduler.schedule()
        Doctor.query.filter(Doctor.doctorStatus != "Active").update({"queuePosition": 0})
        db.session.commit()
        flash("Priority CPU Scheduling Applied Successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to apply Priority scheduling.", "danger")

    return redirect(url_for("doctor.doctor_list"))
