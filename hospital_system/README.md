# 🏥 Hospital Care Management System

A robust, enterprise-grade Python application designed to streamline core hospital operations: **patient registration**, **conflict-free appointment scheduling**, and **pharmacy medicine inventory & dispensing** with automated **patient allergy safety cross-checks**.

---

## 🌟 Key Highlights & Engineering Features

- **🛡️ Rock-Solid Architecture**: Built on clean layered architecture separating **Core Database & Exceptions**, **Domain Models**, **Business Logic Services**, and **Presentation (Terminal UI)**.
- **⚡ ACID Database Transactions**: Powered by SQLite with strict foreign key constraints (`PRAGMA foreign_keys = ON;`). Stock decrements, appointment bookings, and prescription fulfillment happen in atomic database transactions with automatic rollback on error.
- **💊 Pharmacy & Medicine Dispensing**:
  - Full medicine catalog with dosage, forms, unit prices, expiration dates, and min safety thresholds.
  - Automated **low-stock alerts** (immediate visual flagging of items needing replenishment).
  - **Allergy Cross-Checking**: Prevents prescribing or dispensing medication that contains active ingredients or substances matching a patient's known allergies.
  - **Atomic Dispensing**: Guarantees medicine stock cannot go below zero. Multi-item prescriptions are validated and fulfilled atomically with itemized receipt generation.
- **📅 Conflict-Free Appointment Scheduling**:
  - Doctor working hours validation.
  - Prevents doctor double-booking (slot collision detection).
  - Prevents patient simultaneous booking conflicts.
  - Appointment lifecycle management: `SCHEDULED`, `COMPLETED` (with consultation notes & immediate prescription drafting), `CANCELLED`, and rescheduling.
- **🎨 Interactive Rich Console UI**: Polished, color-coded terminal interface with tables, badges, confirmation prompts, and KPI dashboard.
- **🧪 100% Automated Test Suite**: Built with Python's standard `unittest` framework covering CRUD, conflict detection, transaction rollbacks, and edge cases.
- **🌱 Realistic Seed Dataset**: Comes ready with pre-configured doctors, patients, medicine inventory, and appointments for immediate hands-on testing.

---

## 📁 Project Architecture

```
hospital_system/
├── core/
│   ├── database.py         # SQLite connection, transaction manager & schema DDL
│   ├── exceptions.py       # Domain-specific custom exceptions
│   └── __init__.py
├── models/
│   ├── patient.py          # Patient model (age calculation, allergy matching)
│   ├── doctor.py           # Doctor model (working hours check)
│   ├── appointment.py      # Appointment model
│   ├── medicine.py         # Medicine model (stock status, expiration check)
│   ├── prescription.py     # Prescription, PrescriptionItem & DispenseRecord
│   └── __init__.py
├── services/
│   ├── patient_service.py      # Patient validation, registration & search
│   ├── doctor_service.py       # Doctor registry, specialties & slot availability
│   ├── appointment_service.py  # Conflict detection & appointment lifecycle
│   ├── pharmacy_service.py     # Medicine stock, allergy checks & atomic dispensing
│   └── __init__.py
├── ui/
│   ├── console.py          # Rich formatting, prompts, errors, and warnings
│   ├── views.py            # Formatted tables, patient cards, receipts & dashboard
│   ├── menu.py             # Interactive CLI navigation and workflow controllers
│   └── __init__.py
├── tests/
│   ├── test_patients.py        # Patient CRUD & validation unit tests
│   ├── test_appointments.py    # Slot collision & scheduling unit tests
│   ├── test_pharmacy.py        # Inventory, allergy alert & dispensing tests
│   └── __init__.py
├── data/
│   └── hospital.db         # Persistent SQLite database (auto-generated)
├── seed_data.py            # Realistic demonstration dataset
├── main.py                 # CLI entry point
└── README.md               # Documentation
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+ (tested with Python 3.13)
- Dependencies: `rich` (installed by default or via `pip install rich`)

### 2. Launch the Application
You can run the application directly from the repository root:

```bash
# Launch interactive application
python3 run_hospital.py
```
Or directly from the module:
```bash
python3 hospital_system/main.py
```

### 3. Run the Automated Test Suite
To verify that all components are functioning as expected:

```bash
python3 hospital_system/main.py --test
```
Or with unittest directly:
```bash
python3 -m unittest discover -s hospital_system/tests -v
```

### 4. CLI Flags
- `--seed`: Force seeding demo data into the database.
- `--reset`: Wipe the database and recreate fresh tables from scratch.
- `--test`: Run the complete test suite.
- `--db <path>`: Specify a custom database path.

Example:
```bash
python3 hospital_system/main.py --reset --seed
```

---

## 🔍 Core Workflows Overview

### 1. Patient Registration & Allergy Profile
Each patient record stores contact info, blood type, and known allergies. When doctors or pharmacists handle medications, this profile is automatically inspected to protect patient health.

### 2. Appointment Booking
When scheduling an appointment:
1. Validates that the appointment date is not in the past.
2. Checks that the doctor is on duty during the selected time slot.
3. Checks that neither the doctor nor the patient already has an active appointment at that exact slot.
4. Generates an appointment code (`APT-XXXX`).

### 3. Prescription Writing & Dispensing
1. **Prescription**: The doctor specifies medications, quantities, and dosage instructions. If the patient is recorded as allergic to any prescribed substance, a **Critical Allergy Alert** is immediately triggered.
2. **Dispensing**: The pharmacy validates current stock levels for every requested item. If sufficient, stock quantities are decremented atomically, prescription status is updated to `DISPENSED`, and an itemized financial receipt is produced.

