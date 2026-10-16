# Smart Hospital Resource Management And Reallocation System
## Unified Master Integration (Milestone 40%)

### 👥 Team Contribution & OS Concept Mapping

| Module | Student Name | Responsibility / Feature | Operating Systems Concept & Algorithm |
| :--- | :--- | :--- | :--- |
| **Module 1** | **Palak Rawat** | User Authentication & Master Dashboard | **Process Synchronization & Session Lock (Mutex)** |
| **Module 2** | **Prasoon Joshi** | Patient Records & Lifecycle State Machine | **Process Control Block (PCB) Representation** |
| **Module 3** | **Yash Yadav** | Doctor Directory & Queue Reallocation | **FCFS & Non-Preemptive Priority CPU Scheduling** |
| **Module 4** | **Sujal Kumar** | Bed & Ward Management, Transfers | **Memory Management (Dynamic Partitioning)** |
| **Module 5** | **Kanishk Ramola** | Medical Equipment Inventory & Allocation | **Banker's Algorithm & Mutex Synchronization** |
| **Module 6** | **Himesh Kathait** | Reports, Resource Monitoring & Audit Logs | **Resource Allocation Graph (RAG) & Deadlock Detection** |

---

### 📂 Architecture Overview

```
master_hospital_system/
├── config.py                               # Database URI and Flask environment settings
├── extensions.py                           # SQLAlchemy and LoginManager instances
├── app.py                                  # Blueprint registration and factory setup
├── run.py                                  # Server startup script
├── requirements.txt                        # Python dependencies
│
├── database/
│   ├── master_schema.sql                   # MySQL relational schema DDL
│   └── seed_data.py                        # Automated database seed script
│
├── models/                                 # Shared relational models for DB integrity
│   ├── user.py, patient.py, doctor.py, ward.py, bed.py, equipment.py, deadlock_log.py, appointment.py
│
├── modules/                                # Teammate code organized by Name & OS Concept
│   ├── module1_palak_auth/                 # Palak Rawat (Auth & Mutex)
│   ├── module2_prasoon_patient/            # Prasoon Joshi (Patient PCB)
│   ├── module3_yash_cpu_scheduling/        # Yash Yadav (CPU Scheduling)
│   ├── module4_sujal_memory_mgmt/          # Sujal Kumar (Memory Management)
│   ├── module5_kanishk_bankers/            # Kanishk Ramola (Banker's Algorithm)
│   └── module6_himesh_deadlock_reports/    # Himesh Kathait (Deadlock Detection & RAG)
│
├── templates/                              # Bootstrap 5 UI views for all modules
└── tests/                                  # 100% passing automated test suite (49/49)
```

---

### 🚀 Quick Start Guide

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Database Setup (MySQL)
Ensure your local MySQL service is running on `localhost:3306` with database `hospital_db`.
To apply the schema and seed data:
```bash
python database/seed_data.py
```

#### 3. Run the Application
```bash
python run.py
```
Open **`http://127.0.0.1:5000`** in your browser.

#### 4. Default Login Credentials
- **Username:** `admin`
- **Password:** `admin123`

---

### 🧪 Running the Verification Test Suite

To verify that all 6 modules and all OS algorithms are functioning properly:
```bash
python tests/test_master_suite.py
```
*(All 49 unit tests will execute and confirm system integrity)*
