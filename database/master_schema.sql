-- ============================================================================
-- SMART HOSPITAL RESOURCE MANAGEMENT AND REALLOCATION SYSTEM
-- Master Consolidated MySQL Database Schema
-- Modules:
--   1. User Auth & Session Management (Palak Rawat)
--   2. Patient Management & PCB Lifecycle (Prasoon Joshi)
--   3. Doctor Management & CPU Scheduling (Yash Yadav)
--   4. Bed & Ward Management & Dynamic Partitioning (Sujal Kumar)
--   5. Medical Equipment & Banker's Algorithm (Kanishk Ramola)
--   6. Resource Reports & Deadlock Logs (Himesh Kathait)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- ----------------------------------------------------------------------------
-- 1. Palak Rawat: Users & Auth Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_role VARCHAR(30) NOT NULL DEFAULT 'Admin',
    login_status VARCHAR(20) DEFAULT 'Logged Out',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. Prasoon Joshi: Patients Table (Process PCB representation)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    patientName VARCHAR(100) NOT NULL,
    patientStatus VARCHAR(50) DEFAULT 'Waiting', -- Waiting, Admitted, Discharged
    assignedWard VARCHAR(100) NULL,
    assignedBed VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. Yash Yadav: Doctors Table (CPU Scheduling entities)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    doctor_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    experience_years INT DEFAULT 0,
    availability_status VARCHAR(30) DEFAULT 'Available',
    priority_level VARCHAR(20) DEFAULT 'Medium', -- Emergency, High, Medium, Low
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 4. Sujal Kumar: Wards (Memory Partitions) & Beds (Page Frames)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wards (
    ward_id INT PRIMARY KEY AUTO_INCREMENT,
    wardName VARCHAR(100) UNIQUE NOT NULL,
    wardType VARCHAR(50) NOT NULL,
    wardCapacity INT NOT NULL DEFAULT 10,
    occupiedBeds INT DEFAULT 0,
    availableBeds INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS beds (
    bed_id INT PRIMARY KEY AUTO_INCREMENT,
    bedNumber VARCHAR(50) UNIQUE NOT NULL,
    bedType VARCHAR(50) NOT NULL,
    bedStatus VARCHAR(30) DEFAULT 'Available', -- Available, Occupied, Reserved, Maintenance
    bedAvailability BOOLEAN DEFAULT TRUE,
    assignedPatient VARCHAR(100) NULL,
    assignedWard VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 5. Kanishk Ramola: Equipment, Allocations & Banker's Algorithm Claims
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS equipment (
    equipmentId INT AUTO_INCREMENT PRIMARY KEY,
    equipmentName VARCHAR(100) NOT NULL,
    equipmentType VARCHAR(100) NOT NULL,
    equipmentStatus ENUM('Available', 'In Use', 'Maintenance', 'Unavailable') DEFAULT 'Available',
    equipmentAvailability INT DEFAULT 1,
    equipmentLocation VARCHAR(100) NOT NULL,
    maintenanceDate DATE NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS equipment_allocation (
    allocationId INT AUTO_INCREMENT PRIMARY KEY,
    equipmentId INT NOT NULL,
    patientId VARCHAR(50) NOT NULL,
    allocatedResources INT DEFAULT 0,
    requestedResources INT DEFAULT 0,
    resourceStatus ENUM('Allocated', 'Waiting', 'Released', 'Denied') DEFAULT 'Allocated',
    allocatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    releasedAt TIMESTAMP NULL,
    FOREIGN KEY (equipmentId) REFERENCES equipment(equipmentId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS patient_resource_claim (
    claimId INT AUTO_INCREMENT PRIMARY KEY,
    patientId VARCHAR(50) NOT NULL,
    equipmentId INT NOT NULL,
    maximumNeed INT NOT NULL,
    allocatedNeed INT DEFAULT 0,
    remainingNeed INT GENERATED ALWAYS AS (maximumNeed - allocatedNeed) STORED,
    FOREIGN KEY (equipmentId) REFERENCES equipment(equipmentId) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 6. Himesh Kathait: Deadlock Logs & Appointments (Resource Allocation Graph Logs)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deadlock_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    waitingQueue TEXT NULL,
    blockedProcesses TEXT NULL,
    resourceGraph TEXT NULL,
    deadlockStatus VARCHAR(50) DEFAULT 'No Deadlock',
    detectedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NULL,
    doctor_id INT NULL,
    appointmentDate DATE NULL,
    appointmentTime VARCHAR(20) NULL,
    appointmentStatus VARCHAR(30) DEFAULT 'Confirmed', -- Pending, Confirmed, Completed, Cancelled
    appointmentReason VARCHAR(255) NULL,
    appointmentType VARCHAR(50) DEFAULT 'General', -- Emergency, General, Follow-up
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
