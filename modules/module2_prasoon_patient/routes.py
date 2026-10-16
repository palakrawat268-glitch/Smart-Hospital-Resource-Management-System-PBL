# modules/module2_prasoon_patient/routes.py
# Author: Prasoon Joshi
# Module 2: Patient Registration & Process Lifecycle (PCB Representation)

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from .models import Patient

patient_bp = Blueprint("patient", __name__, url_prefix="/patients")


@patient_bp.route("/")
@login_required
def patient_list():
    searchQuery = request.args.get("search", "").strip().lower()
    statusFilter = request.args.get("status", "").strip()

    patients = Patient.query.all()

    if searchQuery:
        patients = [p for p in patients if searchQuery in (p.patientName or "").lower()]

    if statusFilter:
        patients = [p for p in patients if p.patientStatus == statusFilter]

    return render_template(
        "patients/patient_list.html",
        patients=patients,
        searchQuery=searchQuery,
        statusFilter=statusFilter
    )


@patient_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        patientName = request.form.get("patientName", "").strip()
        patientStatus = request.form.get("patientStatus", "Waiting").strip()

        if not patientName:
            flash("Patient name is required!", "warning")
            return redirect(url_for("patient.add_patient"))

        newPatient = Patient(
            patientName=patientName,
            patientStatus=patientStatus,
            assignedWard=None,
            assignedBed=None
        )

        try:
            db.session.add(newPatient)
            db.session.commit()
            flash(f"Patient '{patientName}' registered successfully (Status: {patientStatus})!", "success")
            return redirect(url_for("patient.patient_list"))
        except Exception:
            db.session.rollback()
            flash("Failed to register patient.", "danger")
            return redirect(url_for("patient.add_patient"))

    return render_template("patients/patient_form.html", patient=None, action="Add")


@patient_bp.route("/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def edit_patient(pid):
    patient = db.session.get(Patient, pid)
    if not patient:
        flash("Patient not found!", "danger")
        return redirect(url_for("patient.patient_list"))

    if request.method == "POST":
        patientName = request.form.get("patientName", "").strip()
        patientStatus = request.form.get("patientStatus", patient.patientStatus).strip()

        if not patientName:
            flash("Patient name is required!", "warning")
            return redirect(url_for("patient.edit_patient", pid=pid))

        patient.patientName = patientName
        patient.patientStatus = patientStatus

        try:
            db.session.commit()
            flash(f"Patient '{patient.patientName}' updated successfully!", "success")
            return redirect(url_for("patient.patient_list"))
        except Exception:
            db.session.rollback()
            flash("Failed to update patient.", "danger")
            return redirect(url_for("patient.edit_patient", pid=pid))

    return render_template("patients/patient_form.html", patient=patient, action="Edit")


@patient_bp.route("/delete/<int:pid>")
@login_required
def delete_patient(pid):
    patient = db.session.get(Patient, pid)
    if not patient:
        flash("Patient not found!", "danger")
        return redirect(url_for("patient.patient_list"))

    if patient.patientStatus == "Admitted":
        flash("Cannot delete an admitted patient! Discharge from bed first.", "danger")
        return redirect(url_for("patient.patient_list"))

    try:
        db.session.delete(patient)
        db.session.commit()
        flash(f"Patient '{patient.patientName}' deleted successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to delete patient.", "danger")

    return redirect(url_for("patient.patient_list"))
