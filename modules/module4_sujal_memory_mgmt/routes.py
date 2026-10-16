# modules/module4_sujal_memory_mgmt/routes.py
# Author: Sujal Kumar
# Module 4: Bed & Ward Management (OS Memory Management / Dynamic Partitioning)

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from extensions import db
from .models import Ward, Bed
from models.patient import Patient

bed_bp = Blueprint('bed', __name__, url_prefix='/beds')


# ============================================================================
# HELPER: Recalculate Ward Occupancy (Dynamic Memory Partition Frame Accounting)
# ============================================================================
def recalc_ward_occupancy(wardName):
    ward = Ward.query.filter_by(wardName=wardName).first()
    if not ward:
        return

    occupied = Bed.query.filter_by(assignedWard=wardName, bedStatus='Occupied').count()
    reserved = Bed.query.filter_by(assignedWard=wardName, bedStatus='Reserved').count()
    maintenance = Bed.query.filter_by(assignedWard=wardName, bedStatus='Maintenance').count()

    ward.occupiedBeds = occupied
    ward.availableBeds = max(0, (ward.wardCapacity or 0) - occupied - reserved - maintenance)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


# ============================================================================
# ROUTE 1: BED & WARD DASHBOARD
# ============================================================================
@bed_bp.route('/')
@bed_bp.route('/dashboard')
@login_required
def dashboard():
    totalWards = Ward.query.count()
    totalBeds = Bed.query.count()

    availableBeds = Bed.query.filter_by(bedStatus='Available').count()
    occupiedBeds = Bed.query.filter_by(bedStatus='Occupied').count()
    reservedBeds = Bed.query.filter_by(bedStatus='Reserved').count()
    maintenanceBeds = Bed.query.filter_by(bedStatus='Maintenance').count()

    totalCapacity = sum([w.wardCapacity or 0 for w in Ward.query.all()])
    occupancyRate = round((occupiedBeds / totalCapacity) * 100, 1) if totalCapacity else 0

    criticalWards = []
    for w in Ward.query.all():
        if w.wardCapacity and w.wardCapacity > 0 and w.occupiedBeds is not None:
            if (w.occupiedBeds / w.wardCapacity) > 0.8:
                criticalWards.append(w)

    stats = {
        "totalWards": totalWards,
        "totalBeds": totalBeds,
        "availableBeds": availableBeds,
        "occupiedBeds": occupiedBeds,
        "reservedBeds": reservedBeds,
        "maintenanceBeds": maintenanceBeds,
        "totalCapacity": totalCapacity,
        "occupancyRate": occupancyRate
    }

    return render_template(
        "beds/dashboard.html",
        stats=stats,
        criticalWards=criticalWards,
        now=datetime.now()
    )


# ============================================================================
# ROUTE 2: WARD LIST
# ============================================================================
@bed_bp.route("/wards")
@login_required
def ward_list():
    searchQuery = request.args.get("search", "").strip().lower()
    wards = Ward.query.all()

    if searchQuery:
        wards = [
            w for w in wards
            if searchQuery in (w.wardName or "").lower()
            or searchQuery in (w.wardType or "").lower()
        ]

    return render_template("beds/ward_list.html", wards=wards, searchQuery=searchQuery)


# ============================================================================
# ROUTE 3: ADD WARD (CREATE PARTITION)
# ============================================================================
@bed_bp.route("/wards/add", methods=["GET", "POST"])
@login_required
def add_ward():
    if request.method == "POST":
        wardName = request.form.get("wardName", "").strip()
        wardType = request.form.get("wardType", "").strip()
        wardCapacity = request.form.get("wardCapacity", type=int)

        if not wardName or not wardType or wardCapacity is None:
            flash("All fields are required!", "danger")
            return redirect(url_for("bed.add_ward"))

        if wardCapacity <= 0:
            flash("Capacity must be a positive number!", "danger")
            return redirect(url_for("bed.add_ward"))

        existing = Ward.query.filter_by(wardName=wardName).first()
        if existing:
            flash(f"Ward '{wardName}' already exists!", "warning")
            return redirect(url_for("bed.add_ward"))

        newWard = Ward(
            wardName=wardName,
            wardType=wardType,
            wardCapacity=wardCapacity,
            occupiedBeds=0,
            availableBeds=wardCapacity
        )

        try:
            db.session.add(newWard)
            db.session.commit()
            flash(f"Ward '{wardName}' added successfully!", "success")
            return redirect(url_for("bed.ward_list"))
        except IntegrityError:
            db.session.rollback()
            flash(f"Ward '{wardName}' already exists!", "danger")
            return redirect(url_for("bed.add_ward"))
        except Exception:
            db.session.rollback()
            flash("Failed to add ward.", "danger")
            return redirect(url_for("bed.add_ward"))

    return render_template("beds/ward_form.html", ward=None, action="Add")


# ============================================================================
# ROUTE 4: EDIT WARD (RESIZE PARTITION)
# ============================================================================
@bed_bp.route('/wards/edit/<int:wid>', methods=['GET', 'POST'])
@login_required
def edit_ward(wid):
    ward = db.session.get(Ward, wid)
    if not ward:
        flash("Ward not found!", "danger")
        return redirect(url_for('bed.ward_list'))

    if request.method == 'POST':
        wardName = request.form.get('wardName', '').strip()
        wardType = request.form.get('wardType', '').strip()
        newCapacity = request.form.get('wardCapacity', type=int)

        if not wardName or not wardType or newCapacity is None or newCapacity <= 0:
            flash("Invalid input!", "danger")
            return redirect(url_for('bed.edit_ward', wid=wid))

        if newCapacity < (ward.occupiedBeds or 0):
            flash(f"Cannot reduce capacity below current occupied beds ({ward.occupiedBeds})!", "danger")
            return redirect(url_for('bed.edit_ward', wid=wid))

        total_beds = Bed.query.filter_by(assignedWard=ward.wardName).count()
        if newCapacity < total_beds:
            flash(f"Cannot reduce capacity ({newCapacity}) below total existing beds ({total_beds}) in this ward! Delete beds first.", "danger")
            return redirect(url_for('bed.edit_ward', wid=wid))

        old_name = ward.wardName
        ward.wardName = wardName
        ward.wardType = wardType
        ward.wardCapacity = newCapacity
        ward.availableBeds = max(0, newCapacity - (ward.occupiedBeds or 0))

        if wardName != old_name:
            Bed.query.filter_by(assignedWard=old_name).update({'assignedWard': wardName})

        try:
            db.session.commit()
            flash(f"Ward '{ward.wardName}' updated successfully!", "success")
            return redirect(url_for('bed.ward_list'))
        except IntegrityError:
            db.session.rollback()
            flash("Another ward already has this name.", "danger")
            return redirect(url_for('bed.edit_ward', wid=wid))
        except Exception:
            db.session.rollback()
            flash("Failed to update ward.", "danger")
            return redirect(url_for('bed.edit_ward', wid=wid))

    return render_template('beds/ward_form.html', ward=ward, action='Edit')


# ============================================================================
# ROUTE 5: DELETE WARD
# ============================================================================
@bed_bp.route('/wards/delete/<int:wid>')
@login_required
def delete_ward(wid):
    ward = db.session.get(Ward, wid)
    if not ward:
        flash("Ward not found!", "danger")
        return redirect(url_for('bed.ward_list'))

    attachedBeds = Bed.query.filter_by(assignedWard=ward.wardName).count()
    if attachedBeds > 0:
        flash(f"Cannot delete '{ward.wardName}' — {attachedBeds} bed(s) attached. Remove beds first.", "danger")
        return redirect(url_for('bed.ward_list'))

    try:
        db.session.delete(ward)
        db.session.commit()
        flash(f"Ward '{ward.wardName}' deleted!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to delete ward.", "danger")

    return redirect(url_for('bed.ward_list'))


# ============================================================================
# ROUTE 6: BED LIST (PAGE FRAMES IN PARTITIONS)
# ============================================================================
@bed_bp.route('/beds')
@login_required
def bed_list():
    searchQuery = request.args.get('search', '').strip().lower()
    wardFilter = request.args.get('ward', '').strip()
    statusFilter = request.args.get('status', '').strip()

    beds = Bed.query.all()
    wards = Ward.query.all()

    if searchQuery:
        beds = [
            b for b in beds
            if searchQuery in (b.bedNumber or '').lower()
            or searchQuery in (b.bedType or '').lower()
        ]

    if wardFilter:
        beds = [b for b in beds if b.assignedWard == wardFilter]

    if statusFilter:
        beds = [b for b in beds if b.bedStatus == statusFilter]

    return render_template(
        'beds/bed_list.html',
        beds=beds,
        wards=wards,
        searchQuery=searchQuery,
        wardFilter=wardFilter,
        statusFilter=statusFilter
    )


# ============================================================================
# ROUTE 7: ADD BED (CREATE PAGE FRAME)
# ============================================================================
@bed_bp.route('/beds/add', methods=['GET', 'POST'])
@login_required
def add_bed():
    wards = Ward.query.all()

    if request.method == 'POST':
        bedNumber = request.form.get('bedNumber', '').strip()
        bedType = request.form.get('bedType', '').strip()
        bedStatus = request.form.get('bedStatus', 'Available')
        assignedWard = request.form.get('assignedWard', '').strip()

        if not bedNumber or not bedType or not assignedWard:
            flash("All fields are required!", "danger")
            return redirect(url_for('bed.add_bed'))

        if bedStatus not in ['Available', 'Occupied', 'Reserved', 'Maintenance']:
            flash("Invalid bed status!", "danger")
            return redirect(url_for('bed.add_bed'))

        existing = Bed.query.filter_by(bedNumber=bedNumber).first()
        if existing:
            flash(f"Bed '{bedNumber}' already exists!", "warning")
            return redirect(url_for('bed.add_bed'))

        ward = Ward.query.filter_by(wardName=assignedWard).first()
        if not ward:
            flash("Selected ward does not exist!", "danger")
            return redirect(url_for('bed.add_bed'))

        currentBedsInWard = Bed.query.filter_by(assignedWard=assignedWard).count()
        if currentBedsInWard >= (ward.wardCapacity or 0):
            flash(f"Ward '{assignedWard}' is at full capacity ({ward.wardCapacity})!", "danger")
            return redirect(url_for('bed.add_bed'))

        newBed = Bed(
            bedNumber=bedNumber,
            bedType=bedType,
            bedStatus=bedStatus,
            bedAvailability=(bedStatus == 'Available'),
            assignedWard=assignedWard,
            assignedPatient=None
        )

        try:
            db.session.add(newBed)
            db.session.commit()
            recalc_ward_occupancy(assignedWard)
            flash(f"Bed '{bedNumber}' added to '{assignedWard}'!", "success")
            return redirect(url_for('bed.bed_list'))
        except IntegrityError:
            db.session.rollback()
            flash(f"Bed '{bedNumber}' already exists!", "danger")
            return redirect(url_for('bed.add_bed'))
        except Exception:
            db.session.rollback()
            flash("Failed to add bed.", "danger")
            return redirect(url_for('bed.add_bed'))

    return render_template('beds/bed_form.html', bed=None, wards=wards, action='Add')


# ============================================================================
# ROUTE 8: EDIT BED
# ============================================================================
@bed_bp.route('/beds/edit/<int:bid>', methods=['GET', 'POST'])
@login_required
def edit_bed(bid):
    bed = db.session.get(Bed, bid)
    wards = Ward.query.all()

    if not bed:
        flash("Bed not found!", "danger")
        return redirect(url_for('bed.bed_list'))

    if request.method == 'POST':
        oldWard = bed.assignedWard
        bedNumber = request.form.get('bedNumber', '').strip()
        bedType = request.form.get('bedType', '').strip()
        newStatus = request.form.get('bedStatus', bed.bedStatus)
        newWardName = request.form.get('assignedWard', bed.assignedWard)

        collision = Bed.query.filter(Bed.bedNumber == bedNumber, Bed.bed_id != bid).first()
        if collision:
            flash(f"Another bed already uses number '{bedNumber}'!", "danger")
            return redirect(url_for('bed.edit_bed', bid=bid))

        if newWardName != oldWard:
            targetWard = Ward.query.filter_by(wardName=newWardName).first()
            if not targetWard:
                flash("Selected target ward does not exist!", "danger")
                return redirect(url_for('bed.edit_bed', bid=bid))
            currentBedsInTarget = Bed.query.filter_by(assignedWard=newWardName).count()
            if currentBedsInTarget >= (targetWard.wardCapacity or 0):
                flash(f"Target ward '{newWardName}' is at full capacity ({targetWard.wardCapacity})!", "danger")
                return redirect(url_for('bed.edit_bed', bid=bid))

        bed.bedNumber = bedNumber
        bed.bedType = bedType
        bed.bedStatus = newStatus
        bed.bedAvailability = (newStatus == 'Available')
        bed.assignedWard = newWardName

        try:
            db.session.commit()
            recalc_ward_occupancy(oldWard)
            if newWardName != oldWard:
                recalc_ward_occupancy(newWardName)
            flash(f"Bed '{bed.bedNumber}' updated successfully!", "success")
            return redirect(url_for('bed.bed_list'))
        except Exception:
            db.session.rollback()
            flash("Failed to update bed.", "danger")
            return redirect(url_for('bed.edit_bed', bid=bid))

    return render_template('beds/bed_form.html', bed=bed, wards=wards, action='Edit')


# ============================================================================
# ROUTE 9: DELETE BED
# ============================================================================
@bed_bp.route('/beds/delete/<int:bid>')
@login_required
def delete_bed(bid):
    bed = db.session.get(Bed, bid)
    if not bed:
        flash("Bed not found!", "danger")
        return redirect(url_for('bed.bed_list'))

    if bed.bedStatus == 'Occupied':
        flash("Cannot delete an occupied bed! Discharge patient first.", "danger")
        return redirect(url_for('bed.bed_list'))

    wardName = bed.assignedWard
    try:
        db.session.delete(bed)
        db.session.commit()
        recalc_ward_occupancy(wardName)
        flash(f"Bed '{bed.bedNumber}' deleted!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to delete bed.", "danger")

    return redirect(url_for('bed.bed_list'))


# ============================================================================
# ROUTE 10: ASSIGN BED (DYNAMIC MEMORY ALLOCATION)
# ============================================================================
@bed_bp.route('/beds/assign/<int:bid>', methods=['GET', 'POST'])
@login_required
def assign_bed(bid):
    bed = db.session.get(Bed, bid)
    if not bed:
        flash("Bed not found!", "danger")
        return redirect(url_for('bed.bed_list'))

    if bed.bedStatus != 'Available':
        flash(f"Bed '{bed.bedNumber}' is not available for assignment (current status: {bed.bedStatus})!", "danger")
        return redirect(url_for('bed.bed_list'))

    patients = Patient.query.filter_by(patientStatus='Waiting').all()

    if request.method == "POST":
        patientName = request.form.get("assignedPatient", "").strip()

        if not patientName:
            flash("Please enter or select a patient name!", "warning")
            return redirect(url_for('bed.assign_bed', bid=bid))

        already_holding = Bed.query.filter_by(assignedPatient=patientName, bedStatus="Occupied").first()
        if already_holding and already_holding.bed_id != bed.bed_id:
            flash(f"Patient '{patientName}' is already assigned to Bed '{already_holding.bedNumber}'! Transfer or discharge them first.", "warning")
            return redirect(url_for('bed.assign_bed', bid=bid))

        patient = Patient.query.filter_by(patientName=patientName).first()
        if not patient:
            patient = Patient(patientName=patientName, patientStatus="Waiting")
            db.session.add(patient)
            db.session.commit()

        bed.assignedPatient = patient.patientName
        bed.bedStatus = "Occupied"
        bed.bedAvailability = False

        patient.patientStatus = "Admitted"
        patient.assignedWard = bed.assignedWard
        patient.assignedBed = bed.bedNumber

        try:
            db.session.commit()
            recalc_ward_occupancy(bed.assignedWard)
            flash(f"Bed '{bed.bedNumber}' assigned to '{patient.patientName}' successfully!", "success")
            return redirect(url_for('bed.bed_list'))
        except Exception:
            db.session.rollback()
            flash("Failed to assign bed.", "danger")
            return redirect(url_for('bed.assign_bed', bid=bid))

    return render_template("beds/assign_bed.html", bed=bed, patients=patients)


# ============================================================================
# ROUTE 11: DISCHARGE BED (DYNAMIC MEMORY DEALLOCATION)
# ============================================================================
@bed_bp.route('/beds/discharge/<int:bid>')
@login_required
def discharge_bed(bid):
    bed = db.session.get(Bed, bid)
    if not bed:
        flash("Bed not found!", "danger")
        return redirect(url_for('bed.bed_list'))

    patientName = bed.assignedPatient
    if patientName:
        patient = Patient.query.filter_by(patientName=patientName).first()
        if patient:
            patient.patientStatus = 'Discharged'
            patient.assignedBed = None

    bed.assignedPatient = None
    bed.bedStatus = 'Available'
    bed.bedAvailability = True

    try:
        db.session.commit()
        recalc_ward_occupancy(bed.assignedWard)
        flash(f"Patient discharged from Bed '{bed.bedNumber}'. Bed is now Available!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to discharge bed.", "danger")

    return redirect(url_for('bed.bed_list'))


# ============================================================================
# ROUTE 12: TRANSFER BED (MEMORY FRAME RELOCATION)
# ============================================================================
@bed_bp.route('/beds/transfer/<int:bid>', methods=['GET', 'POST'])
@login_required
def transfer_bed(bid):
    fromBed = db.session.get(Bed, bid)
    if not fromBed or fromBed.bedStatus != 'Occupied':
        flash("Can only transfer from an occupied bed!", "danger")
        return redirect(url_for('bed.bed_list'))

    availableBeds = Bed.query.filter(Bed.bedStatus == 'Available', Bed.bed_id != bid).all()

    if request.method == 'POST':
        toBedId = request.form.get('toBedId', type=int)
        toBed = db.session.get(Bed, toBedId)

        if not toBed or toBed.bedStatus != 'Available':
            flash("Target bed is no longer available!", "danger")
            return redirect(url_for('bed.transfer_bed', bid=bid))

        patientName = fromBed.assignedPatient
        oldWard = fromBed.assignedWard

        toBed.assignedPatient = patientName
        toBed.bedStatus = 'Occupied'
        toBed.bedAvailability = False

        fromBed.assignedPatient = None
        fromBed.bedStatus = 'Available'
        fromBed.bedAvailability = True

        patient = Patient.query.filter_by(patientName=patientName).first()
        if patient:
            patient.assignedWard = toBed.assignedWard
            patient.assignedBed = toBed.bedNumber

        try:
            db.session.commit()
            recalc_ward_occupancy(oldWard)
            recalc_ward_occupancy(toBed.assignedWard)
            flash(f"Transferred '{patientName}' from Bed {fromBed.bedNumber} to Bed {toBed.bedNumber}!", "success")
            return redirect(url_for('bed.bed_list'))
        except Exception:
            db.session.rollback()
            flash("Transfer failed.", "danger")
            return redirect(url_for('bed.transfer_bed', bid=bid))

    return render_template('beds/transfer_bed.html', fromBed=fromBed, availableBeds=availableBeds)


# ============================================================================
# ROUTE 13: UPDATE STATUS (MAINTENANCE / RESERVED)
# ============================================================================
@bed_bp.route('/beds/status/<int:bid>', methods=['POST'])
@login_required
def update_bed_status(bid):
    bed = db.session.get(Bed, bid)
    if not bed:
        flash("Bed not found!", "danger")
        return redirect(url_for('bed.bed_list'))

    newStatus = request.form.get('status')
    if newStatus not in ['Available', 'Reserved', 'Maintenance']:
        flash("Invalid status transition!", "danger")
        return redirect(url_for('bed.bed_list'))

    if bed.bedStatus == 'Occupied':
        flash("Cannot change status of occupied bed! Discharge first.", "danger")
        return redirect(url_for('bed.bed_list'))

    bed.bedStatus = newStatus
    bed.bedAvailability = (newStatus == 'Available')

    try:
        db.session.commit()
        recalc_ward_occupancy(bed.assignedWard)
        flash(f"Bed '{bed.bedNumber}' status set to '{newStatus}'!", "success")
    except Exception:
        db.session.rollback()
        flash("Failed to update status.", "danger")

    return redirect(url_for('bed.bed_list'))


# ============================================================================
# ROUTE 14: API STATS (FOR REPORT & CHARTS INTEGRATION)
# ============================================================================
@bed_bp.route('/api/stats')
def api_stats():
    totalWards = Ward.query.count()
    totalBeds = Bed.query.count()
    availableBeds = Bed.query.filter_by(bedStatus='Available').count()
    occupiedBeds = Bed.query.filter_by(bedStatus='Occupied').count()

    return jsonify({
        "totalWards": totalWards,
        "totalBeds": totalBeds,
        "availableBeds": availableBeds,
        "occupiedBeds": occupiedBeds
    }), 200
