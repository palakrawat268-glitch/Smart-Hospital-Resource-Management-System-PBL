# modules/module5_kanishk_bankers/routes.py
# Author: Kanishk Ramola
# Module 5: Medical Equipment Management & Banker's Algorithm (Deadlock Avoidance)

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from extensions import db
from .models import Equipment, EquipmentAllocation, PatientResourceClaim
from .os_core.bankers_algorithm import BankersAlgorithm
from .os_core.deadlock_detector import DeadlockDetector
from .os_core.synchronization import equipment_sync
from models.deadlock_log import DeadlockLog

equipment_bp = Blueprint("equipment", __name__, url_prefix="")


def build_bankers_matrices():
    equipment_list = Equipment.query.order_by(Equipment.equipmentId).all()
    claims = PatientResourceClaim.query.all()
    allocations = EquipmentAllocation.query.filter_by(resourceStatus='Allocated').all()

    if not equipment_list or not claims:
        return None, [], []

    eq_map = {eq.equipmentId: idx for idx, eq in enumerate(equipment_list)}
    available = [eq.equipmentAvailability or 0 for eq in equipment_list]

    patients = sorted(list(set(c.patientId for c in claims)))
    p_map = {p: idx for idx, p in enumerate(patients)}

    num_p = len(patients)
    num_r = len(equipment_list)

    max_matrix = [[0] * num_r for _ in range(num_p)]
    alloc_matrix = [[0] * num_r for _ in range(num_p)]

    for c in claims:
        p_idx = p_map.get(c.patientId)
        r_idx = eq_map.get(c.equipmentId)
        if p_idx is not None and r_idx is not None:
            max_matrix[p_idx][r_idx] = c.maximumNeed or 0
            alloc_matrix[p_idx][r_idx] = c.allocatedNeed or 0

    banker = BankersAlgorithm(available, max_matrix, alloc_matrix, process_names=patients)
    return banker, equipment_list, patients


# ============================================================================
# EQUIPMENT INVENTORY
# ============================================================================

@equipment_bp.route("/inventory")
@login_required
def inventory():
    equipment_list = Equipment.query.all()
    total_items = len(equipment_list)
    available_items = sum(1 for e in equipment_list if e.equipmentStatus == 'Available')
    in_use_items = sum(1 for e in equipment_list if e.equipmentStatus == 'In Use')
    maintenance_items = sum(1 for e in equipment_list if e.equipmentStatus == 'Maintenance')

    stats = {
        'totalEquipment': total_items,
        'availableEquipment': available_items,
        'inUseEquipment': in_use_items,
        'maintenanceEquipment': maintenance_items
    }

    return render_template(
        "equipment/inventory.html",
        equipment_list=equipment_list,
        stats=stats
    )


@equipment_bp.route("/equipment/add", methods=["POST"])
@login_required
def add_equipment():
    name = request.form.get("equipmentName", "").strip()
    eq_type = request.form.get("equipmentType", "").strip()
    status = request.form.get("equipmentStatus", "Available")
    availability = int(request.form.get("equipmentAvailability", 1))
    location = request.form.get("equipmentLocation", "").strip()
    m_date = request.form.get("maintenanceDate") or None

    if not name or not eq_type or not location:
        flash("Please fill in all required equipment details.", "warning")
        return redirect(url_for("equipment.inventory"))

    new_eq = Equipment(
        equipmentName=name,
        equipmentType=eq_type,
        equipmentStatus=status,
        equipmentAvailability=availability,
        equipmentLocation=location,
        maintenanceDate=m_date
    )

    try:
        db.session.add(new_eq)
        db.session.commit()
        flash(f"Equipment '{name}' registered successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("Error adding equipment.", "danger")

    return redirect(url_for("equipment.inventory"))


# ============================================================================
# BANKER'S ALGORITHM ALLOCATION PAGE
# ============================================================================

@equipment_bp.route("/allocation")
@login_required
def allocation_page():
    equipment_list = Equipment.query.all()
    claims = PatientResourceClaim.query.all()
    allocations = EquipmentAllocation.query.all()

    banker, _, patients = build_bankers_matrices()
    os_state = None
    if banker:
        is_safe, seq, logs = banker.is_safe_state()
        os_state = {
            'is_safe': is_safe,
            'safeSequence': seq,
            'logs': logs
        }

    return render_template(
        "equipment/allocation.html",
        equipment_list=equipment_list,
        claims=claims,
        allocations=allocations,
        patient_ids=patients,
        os_state=os_state
    )


@equipment_bp.route("/allocation/allocate", methods=["POST"])
@login_required
def allocate_equipment():
    patient_id = request.form.get("patientId")
    equipment_id = request.form.get("equipmentId")
    requested_qty = request.form.get("requestedResources", 1)

    if not patient_id or not equipment_id:
        flash("Please select both a patient and an equipment.", "warning")
        return redirect(url_for("equipment.allocation_page"))

    try:
        eq_id = int(equipment_id)
        qty = int(requested_qty)
        if qty <= 0:
            flash("Requested quantity must be at least 1.", "warning")
            return redirect(url_for("equipment.allocation_page"))
    except (ValueError, TypeError):
        flash("Invalid resource quantity or equipment selection.", "danger")
        return redirect(url_for("equipment.allocation_page"))

    eq = db.session.get(Equipment, eq_id)
    if not eq:
        flash("Equipment not found.", "danger")
        return redirect(url_for("equipment.allocation_page"))

    with equipment_sync.criticalSection():
        claim = PatientResourceClaim.query.filter_by(patientId=patient_id, equipmentId=eq_id).first()
        if not claim:
            claim = PatientResourceClaim(patientId=patient_id, equipmentId=eq_id, maximumNeed=qty + 2, allocatedNeed=0)
            db.session.add(claim)
            db.session.commit()

        remaining = (claim.maximumNeed or 0) - (claim.allocatedNeed or 0)
        if qty > remaining:
            flash(f"BLOCKED: Request ({qty}) exceeds remaining declared need ({remaining})!", "danger")
            return redirect(url_for("equipment.allocation_page"))

        if qty > (eq.equipmentAvailability or 0):
            flash(f"BLOCKED: Insufficient available units of {eq.equipmentName} ({eq.equipmentAvailability} free). Patient must wait.", "warning")
            return redirect(url_for("equipment.allocation_page"))

        banker, _, patients = build_bankers_matrices()
        if banker and patient_id in patients:
            p_idx = patients.index(patient_id)
            req_vector = [0] * banker.num_resources
            eq_list = Equipment.query.order_by(Equipment.equipmentId).all()
            for idx, item in enumerate(eq_list):
                if item.equipmentId == eq_id:
                    req_vector[idx] = qty

            granted, msg, seq = banker.request_resources(p_idx, req_vector)
            if not granted:
                flash(f"BLOCKED (Deadlock Avoidance): {msg}", "danger")
                return redirect(url_for("equipment.allocation_page"))

        eq.equipmentAvailability = max(0, (eq.equipmentAvailability or 0) - qty)
        if eq.equipmentAvailability == 0:
            eq.equipmentStatus = 'In Use'

        claim.allocatedNeed = (claim.allocatedNeed or 0) + qty

        alloc = EquipmentAllocation(
            equipmentId=eq_id,
            patientId=patient_id,
            allocatedResources=qty,
            requestedResources=qty,
            resourceStatus='Allocated'
        )
        db.session.add(alloc)

        try:
            db.session.commit()
            flash(f"SUCCESS: Allocated {qty} unit(s) of '{eq.equipmentName}' to '{patient_id}' safely!", "success")
        except Exception:
            db.session.rollback()
            flash("Database error during allocation commit.", "danger")

    return redirect(url_for("equipment.allocation_page"))


@equipment_bp.route("/allocation/release/<int:allocation_id>", methods=["POST"])
@login_required
def release_equipment(allocation_id: int):
    alloc = db.session.get(EquipmentAllocation, allocation_id)
    if not alloc or alloc.resourceStatus != 'Allocated':
        flash("Allocation record not found or already released.", "warning")
        return redirect(url_for("equipment.allocation_page"))

    with equipment_sync.criticalSection():
        eq = db.session.get(Equipment, alloc.equipmentId)
        if eq:
            eq.equipmentAvailability = (eq.equipmentAvailability or 0) + alloc.allocatedResources
            eq.equipmentStatus = 'Available'

        claim = PatientResourceClaim.query.filter_by(patientId=alloc.patientId, equipmentId=alloc.equipmentId).first()
        if claim:
            claim.allocatedNeed = max(0, (claim.allocatedNeed or 0) - alloc.allocatedResources)

        alloc.resourceStatus = 'Released'
        try:
            db.session.commit()
            flash(f"Released {alloc.allocatedResources} unit(s) of equipment from {alloc.patientId}.", "info")
        except Exception:
            db.session.rollback()
            flash("Error releasing allocation.", "danger")

    return redirect(url_for("equipment.allocation_page"))


# ============================================================================
# DEADLOCK DETECTION ROUTE
# ============================================================================

@equipment_bp.route("/deadlock-check")
@login_required
def run_deadlock_check():
    equipment_list = Equipment.query.order_by(Equipment.equipmentId).all()
    claims = PatientResourceClaim.query.all()
    allocations = EquipmentAllocation.query.filter_by(resourceStatus='Allocated').all()

    if not equipment_list or not claims:
        flash("No active claims or equipment to run deadlock detection on.", "info")
        return redirect(url_for("equipment.allocation_page"))

    patients = sorted(list(set(c.patientId for c in claims)))
    num_p = len(patients)
    num_r = len(equipment_list)

    eq_map = {eq.equipmentId: idx for idx, eq in enumerate(equipment_list)}
    p_map = {p: idx for idx, p in enumerate(patients)}

    avail = [eq.equipmentAvailability or 0 for eq in equipment_list]
    alloc_mat = [[0] * num_r for _ in range(num_p)]
    req_mat = [[0] * num_r for _ in range(num_p)]

    for a in allocations:
        p_idx = p_map.get(a.patientId)
        r_idx = eq_map.get(a.equipmentId)
        if p_idx is not None and r_idx is not None:
            alloc_mat[p_idx][r_idx] += a.allocatedResources

    for c in claims:
        p_idx = p_map.get(c.patientId)
        r_idx = eq_map.get(c.equipmentId)
        if p_idx is not None and r_idx is not None:
            req_mat[p_idx][r_idx] = max(0, (c.maximumNeed or 0) - (c.allocatedNeed or 0))

    detector = DeadlockDetector(num_p, num_r, avail, alloc_mat, req_mat, process_names=patients)
    has_deadlock, blocked, status = detector.detect_deadlock()

    # Log into database for Himesh's Module 6 Deadlock Audit
    log_entry = DeadlockLog(
        waitingQueue=",".join([p for p in patients if any(req_mat[p_map[p]][j] > 0 for j in range(num_r))]) or "None",
        blockedProcesses=",".join(blocked) if blocked else "None",
        resourceGraph=str(detector.resourceGraph),
        deadlockStatus="Deadlock Detected" if has_deadlock else "No Deadlock"
    )
    try:
        db.session.add(log_entry)
        db.session.commit()
    except Exception:
        db.session.rollback()

    if has_deadlock:
        flash(f"DEADLOCK DETECTED! Blocked processes: {', '.join(blocked)}", "danger")
    else:
        flash(f"DEADLOCK CHECK PASSED: {status} (Logged to Audit)", "success")

    return redirect(url_for("equipment.allocation_page"))


# ============================================================================
# API ENDPOINTS (FOR JSON INTEGRATION)
# ============================================================================

@equipment_bp.route("/api/equipment", methods=["GET"])
def api_equipment():
    equipment_list = Equipment.query.all()
    data = [{
        "equipmentId": e.equipmentId,
        "equipmentName": e.equipmentName,
        "equipmentType": e.equipmentType,
        "equipmentStatus": e.equipmentStatus,
        "equipmentAvailability": e.equipmentAvailability,
        "equipmentLocation": e.equipmentLocation,
        "maintenanceDate": str(e.maintenanceDate) if e.maintenanceDate else None
    } for e in equipment_list]
    return jsonify(data), 200
