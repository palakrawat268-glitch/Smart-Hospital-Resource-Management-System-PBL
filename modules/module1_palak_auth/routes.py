# modules/module1_palak_auth/routes.py
# Author: Palak Rawat
# Module 1: Authentication & Session Management with Central Hospital Dashboard

import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

ALLOWED_ROLES = {"Admin", "Doctor", "Receptionist", "Patient"}


# ============================================================================
# AUTHENTICATION ROUTES (Palak Rawat)
# ============================================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        userRole = request.form.get("userRole", "Patient").strip()

        if not username or len(username) < 3 or len(username) > 50:
            flash("Username must be between 3 and 50 characters long.", "warning")
            return redirect(url_for("auth.register"))

        if not password or len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return redirect(url_for("auth.register"))

        if userRole not in ALLOWED_ROLES:
            flash("Invalid role selected. Please choose a valid role.", "warning")
            return redirect(url_for("auth.register"))

        existingUser = User.query.filter_by(username=username).first()
        if existingUser:
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.register"))

        newUser = User(username=username, user_role=userRole, login_status="Logged Out")
        newUser.set_password(password)

        try:
            db.session.add(newUser)
            db.session.commit()
            flash("Registration Successful! Please login.", "success")
            return redirect(url_for("auth.login"))
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.register"))
        except Exception:
            db.session.rollback()
            flash("An unexpected error occurred during registration. Please try again.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "warning")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            user.login_status = "Logged In"
            sessionId = str(uuid.uuid4())[:8]
            db.session.commit()

            session.clear()
            login_user(user)

            session['username'] = user.username
            session['userRole'] = user.user_role
            session['sessionId'] = sessionId

            flash(f"Welcome back, {user.username}!", "success")

            next_url = request.args.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid Username or Password!", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        current_user.login_status = "Logged Out"
        db.session.commit()

    session.clear()
    logout_user()
    flash("Logged Out Successfully!", "success")
    return redirect(url_for("auth.login"))


# ============================================================================
# CENTRAL DASHBOARD ROUTE (Palak Rawat - Integrates all 6 modules)
# ============================================================================

@dashboard_bp.route("/", endpoint="dashboard")
@login_required
def dashboard_view():
    from models.doctor import Doctor
    from models.bed import Bed
    from models.patient import Patient
    from models.equipment import Equipment
    from models.appointment import Appointment
    from models.equipment import EquipmentAllocation

    totalDoctors = 0
    emergencyCases = 0
    try:
        totalDoctors = Doctor.query.count()
        emergencyCases = Doctor.query.filter_by(priority_level="Emergency").count()
    except Exception:
        pass

    availableBeds = 0
    occupiedBeds = 0
    try:
        availableBeds = Bed.query.filter_by(bedStatus="Available").count()
        occupiedBeds = Bed.query.filter_by(bedStatus="Occupied").count()
    except Exception:
        pass

    availableEquipment = 0
    pendingRequests = 0
    try:
        availableEquipment = Equipment.query.filter_by(equipmentStatus='Available').count()
        pendingRequests = EquipmentAllocation.query.filter_by(resourceStatus='Waiting').count()
    except Exception:
        pass

    totalPatients = 0
    try:
        totalPatients = Patient.query.count()
    except Exception:
        pass

    totalAppointments = 0
    try:
        totalAppointments = Appointment.query.count()
    except Exception:
        pass

    return render_template(
        "dashboard/dashboard.html",
        totalDoctors=totalDoctors,
        totalPatients=totalPatients,
        totalAppointments=totalAppointments,
        availableBeds=availableBeds,
        occupiedBeds=occupiedBeds,
        availableEquipment=availableEquipment,
        pendingRequests=pendingRequests,
        emergencyCases=emergencyCases
    )
