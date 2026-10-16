# modules/module6_himesh_deadlock_reports/routes.py
# Author: Himesh Kathait
# Module 6: Report and Resource Monitoring & Deadlock Detection Audit Logs

import csv
import io
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response,
    jsonify
)
from flask_login import login_required, current_user

from extensions import db
from models.patient import Patient
from models.doctor import Doctor
from models.ward import Ward
from models.bed import Bed
from models.equipment import Equipment, EquipmentAllocation, PatientResourceClaim
from .models import DeadlockLog, Appointment

report_bp = Blueprint('report', __name__, url_prefix='/reports')


# ============================================================================
# HELPER: DASHBOARD STATS
# ============================================================================
def get_dashboard_stats():
    totalPatients = Patient.query.count()
    totalDoctors = Doctor.query.count()
    totalAppointments = Appointment.query.count()

    availableBeds = Bed.query.filter_by(bedStatus='Available').count()
    occupiedBeds = Bed.query.filter_by(bedStatus='Occupied').count()

    availableEquipment = Equipment.query.filter_by(equipmentStatus='Available').count()
    pendingRequests = EquipmentAllocation.query.filter_by(resourceStatus='Waiting').count()
    emergencyCases = Doctor.query.filter_by(priorityLevel='Emergency').count()

    return {
        'totalPatients': totalPatients,
        'totalDoctors': totalDoctors,
        'totalAppointments': totalAppointments,
        'availableBeds': availableBeds,
        'occupiedBeds': occupiedBeds,
        'availableEquipment': availableEquipment,
        'pendingRequests': pendingRequests,
        'emergencyCases': emergencyCases
    }


# ============================================================================
# ROUTE 1: REPORTS DASHBOARD (Himesh Kathait)
# ============================================================================
@report_bp.route('/')
@report_bp.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()

    lowBedWards = []
    for w in Ward.query.all():
        if w.wardCapacity and w.wardCapacity > 0 and w.availableBeds is not None:
            if w.availableBeds < (w.wardCapacity * 0.2):
                lowBedWards.append(w)

    maintenanceEquipment = Equipment.query.filter_by(equipmentStatus='Maintenance').all()

    appointmentSummary = {
        'Pending': Appointment.query.filter_by(appointmentStatus='Pending').count(),
        'Confirmed': Appointment.query.filter_by(appointmentStatus='Confirmed').count(),
        'Completed': Appointment.query.filter_by(appointmentStatus='Completed').count(),
        'Cancelled': Appointment.query.filter_by(appointmentStatus='Cancelled').count()
    }

    return render_template(
        'reports/dashboard.html',
        stats=stats,
        lowBedWards=lowBedWards,
        maintenanceEquipment=maintenanceEquipment,
        appointmentSummary=appointmentSummary,
        now=datetime.now()
    )


# ============================================================================
# ROUTE 2: RESOURCE MONITORING (CENTRALIZED READ-ONLY ASSET VIEW)
# ============================================================================
@report_bp.route('/resources')
@login_required
def resource_monitor():
    searchQuery = request.args.get('search', '').strip().lower()

    beds = Bed.query.all()
    equipment = Equipment.query.all()
    wards = Ward.query.all()

    if searchQuery:
        beds = [b for b in beds if searchQuery in (b.bedNumber or '').lower() or searchQuery in (b.bedType or '').lower()]
        equipment = [e for e in equipment if searchQuery in (e.equipmentName or '').lower() or searchQuery in (e.equipmentType or '').lower()]
        wards = [w for w in wards if searchQuery in (w.wardName or '').lower()]

    return render_template(
        'reports/resource_monitor.html',
        beds=beds,
        equipment=equipment,
        wards=wards,
        searchQuery=searchQuery
    )


# ============================================================================
# ROUTE 3: GENERATE TABULAR REPORT
# ============================================================================
@report_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_report():
    reportData = {}
    reportType = None
    generatedAt = None

    if request.method == 'POST':
        reportType = request.form.get('reportType', 'all')

        if reportType == 'patients':
            reportData['title'] = 'Patient Report'
            reportData['type'] = 'patients'
            reportData['rows'] = Patient.query.all()

        elif reportType == 'doctors':
            reportData['title'] = 'Doctor Report'
            reportData['type'] = 'doctors'
            reportData['rows'] = Doctor.query.all()

        elif reportType == 'appointments':
            reportData['title'] = 'Appointment Report'
            reportData['type'] = 'appointments'
            reportData['rows'] = Appointment.query.all()

        elif reportType == 'beds':
            reportData['title'] = 'Bed & Ward Report'
            reportData['type'] = 'beds'
            reportData['rows'] = Bed.query.all()

        elif reportType == 'equipment':
            reportData['title'] = 'Equipment Report'
            reportData['type'] = 'equipment'
            reportData['rows'] = Equipment.query.all()

        elif reportType == 'resources':
            reportData['title'] = 'Resource Allocation Report'
            reportData['type'] = 'resources'
            reportData['rows'] = EquipmentAllocation.query.all()

        elif reportType == 'deadlock':
            reportData['title'] = 'Deadlock Log Report'
            reportData['type'] = 'deadlock'
            reportData['rows'] = DeadlockLog.query.order_by(DeadlockLog.detectedAt.desc()).all()

        else:
            reportData['title'] = 'Complete Hospital Summary Report'
            reportData['type'] = 'all'
            reportData['stats'] = get_dashboard_stats()

        generatedAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        flash(f"{reportData['title']} generated successfully!", "success")

    return render_template(
        'reports/reports.html',
        reportData=reportData,
        reportType=reportType,
        generatedAt=generatedAt
    )


# ============================================================================
# ROUTE 4: EXPORT CSV (DATA EXPORT PIPELINE)
# ============================================================================
@report_bp.route('/export/csv')
@login_required
def export_csv():
    exportType = request.args.get('type', 'equipment')
    output = io.StringIO()
    writer = csv.writer(output)

    if exportType == 'equipment':
        writer.writerow(['ID', 'Equipment Name', 'Type', 'Status', 'Availability', 'Location', 'Maintenance Date'])
        for e in Equipment.query.all():
            writer.writerow([
                getattr(e, 'equipmentId', getattr(e, 'id', '')),
                e.equipmentName,
                e.equipmentType,
                e.equipmentStatus,
                e.equipmentAvailability,
                e.equipmentLocation,
                e.maintenanceDate
            ])

    elif exportType == 'beds':
        writer.writerow(['ID', 'Bed Number', 'Type', 'Status', 'Availability', 'Assigned Patient', 'Assigned Ward'])
        for b in Bed.query.all():
            writer.writerow([
                getattr(b, 'bed_id', getattr(b, 'id', '')),
                b.bedNumber,
                b.bedType,
                b.bedStatus,
                b.bedAvailability,
                b.assignedPatient or 'None',
                b.assignedWard
            ])

    elif exportType == 'patients':
        writer.writerow(['ID', 'Patient Name', 'Patient Status', 'Assigned Ward', 'Assigned Bed'])
        for p in Patient.query.all():
            writer.writerow([
                getattr(p, 'patient_id', getattr(p, 'id', '')),
                p.patientName,
                p.patientStatus,
                p.assignedWard or 'None',
                p.assignedBed or 'None'
            ])

    elif exportType == 'doctors':
        writer.writerow(['ID', 'Doctor Name', 'Department', 'Experience', 'Priority Level', 'Availability', 'Queue Position'])
        for d in Doctor.query.all():
            writer.writerow([
                getattr(d, 'doctor_id', getattr(d, 'id', '')),
                d.doctorName,
                d.doctorDepartment,
                d.doctorExperience,
                d.priorityLevel,
                d.doctorAvailability,
                d.queuePosition
            ])

    elif exportType == 'appointments':
        writer.writerow(['ID', 'Date', 'Time', 'Status', 'Reason', 'Type'])
        for a in Appointment.query.all():
            writer.writerow([
                getattr(a, 'appointment_id', getattr(a, 'id', '')),
                a.appointmentDate,
                a.appointmentTime,
                a.appointmentStatus,
                a.appointmentReason,
                a.appointmentType
            ])

    elif exportType == 'resources':
        writer.writerow(['ID', 'Equipment ID', 'Patient ID', 'Allocated Resources', 'Requested Resources', 'Status'])
        for r in EquipmentAllocation.query.all():
            writer.writerow([
                getattr(r, 'allocationId', getattr(r, 'id', '')),
                r.equipmentId,
                r.patientId,
                r.allocatedResources,
                r.requestedResources,
                r.resourceStatus
            ])

    elif exportType == 'deadlock':
        writer.writerow(['ID', 'Waiting Queue', 'Blocked Processes', 'Resource Graph', 'Status', 'Detected At'])
        for dl in DeadlockLog.query.order_by(DeadlockLog.detectedAt.desc()).all():
            writer.writerow([
                getattr(dl, 'log_id', getattr(dl, 'id', '')),
                dl.waitingQueue,
                dl.blockedProcesses,
                dl.resourceGraph,
                dl.deadlockStatus,
                dl.detectedAt
            ])

    else:
        writer.writerow(['No data'])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={exportType}_report_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


# ============================================================================
# ROUTE 5: JSON API FOR REAL-TIME CHARTS
# ============================================================================
@report_bp.route('/api/stats')
@login_required
def api_stats():
    return jsonify({
        'stats': get_dashboard_stats(),
        'appointmentStatus': {
            'Pending': Appointment.query.filter_by(appointmentStatus='Pending').count(),
            'Confirmed': Appointment.query.filter_by(appointmentStatus='Confirmed').count(),
            'Completed': Appointment.query.filter_by(appointmentStatus='Completed').count(),
            'Cancelled': Appointment.query.filter_by(appointmentStatus='Cancelled').count()
        },
        'bedStatus': {
            'Available': Bed.query.filter_by(bedStatus='Available').count(),
            'Occupied': Bed.query.filter_by(bedStatus='Occupied').count(),
            'Reserved': Bed.query.filter_by(bedStatus='Reserved').count(),
            'Maintenance': Bed.query.filter_by(bedStatus='Maintenance').count()
        },
        'equipmentStatus': {
            'Available': Equipment.query.filter_by(equipmentStatus='Available').count(),
            'In Use': Equipment.query.filter_by(equipmentStatus='In Use').count(),
            'Maintenance': Equipment.query.filter_by(equipmentStatus='Maintenance').count(),
            'Unavailable': Equipment.query.filter_by(equipmentStatus='Unavailable').count()
        }
    })


# ============================================================================
# ROUTE 6: OS DEADLOCK AUDIT LOGS VIEW
# ============================================================================
@report_bp.route('/deadlock')
@login_required
def deadlock_view():
    logs = DeadlockLog.query.order_by(DeadlockLog.detectedAt.desc()).all()
    activeDeadlocks = [l for l in logs if l.deadlockStatus == 'Deadlock Detected']

    return render_template(
        'reports/deadlock.html',
        logs=logs,
        activeDeadlocks=activeDeadlocks
    )


# ============================================================================
# ROUTE 7: OS BANKER'S ALGORITHM MATRIX VIEW
# ============================================================================
@report_bp.route('/bankers')
@login_required
def bankers_view():
    allocations = EquipmentAllocation.query.all()
    claims = PatientResourceClaim.query.all()

    return render_template(
        'reports/bankers.html',
        allocations=allocations,
        claims=claims
    )
