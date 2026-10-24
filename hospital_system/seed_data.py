"""
Seed script to populate the hospital database with realistic initial data.
Enables immediate testing and out-of-the-box demonstration.
"""

from datetime import date, timedelta
from hospital_system.core.database import DatabaseManager
from hospital_system.services.patient_service import PatientService
from hospital_system.services.doctor_service import DoctorService
from hospital_system.services.appointment_service import AppointmentService
from hospital_system.services.pharmacy_service import PharmacyService


def seed_hospital_data(db: DatabaseManager, quiet: bool = False) -> None:
    """Populates the database with realistic doctors, patients, inventory, and appointments."""
    pat_service = PatientService(db)
    doc_service = DoctorService(db)
    apt_service = AppointmentService(db)
    pharma_service = PharmacyService(db)

    # Check if already seeded
    existing_docs = doc_service.list_doctors(active_only=False)
    if len(existing_docs) >= 3:
        if not quiet:
            print("Database already contains records. Skipping seed.")
        return

    if not quiet:
        print("🌱 Seeding realistic hospital data...")

    # 1. Doctors
    doctors_data = [
        ("Dr. John Watson", "CRM-10021", "Cardiology", "+55 11 98888-1001", "watson@hospitalcare.org", "08:00", "17:00"),
        ("Dr. Meredith Grey", "CRM-10022", "General Surgery", "+55 11 98888-1002", "grey@hospitalcare.org", "08:00", "16:00"),
        ("Dr. Gregory House", "CRM-10023", "Internal Medicine", "+55 11 98888-1003", "house@hospitalcare.org", "09:00", "16:00"),
        ("Dr. Sofia Alcantara", "CRM-10024", "Pediatrics", "+55 11 98888-1004", "sofia@hospitalcare.org", "08:00", "15:00"),
        ("Dr. Derek Shepherd", "CRM-10025", "Neurology", "+55 11 98888-1005", "derek@hospitalcare.org", "09:00", "18:00"),
        ("Dr. Lisa Cuddy", "CRM-10026", "Endocrinology", "+55 11 98888-1006", "cuddy@hospitalcare.org", "08:30", "16:30"),
    ]
    doctors = []
    for d in doctors_data:
        doc = doc_service.register_doctor(
            name=d[0],
            license_number=d[1],
            specialty=d[2],
            phone=d[3],
            email=d[4],
            start_time=d[5],
            end_time=d[6],
        )
        doctors.append(doc)

    # 2. Patients
    patients_data = [
        ("Carlos Silva", "111.222.333-44", "1985-04-12", "+55 11 97777-2001", "carlos.silva@email.com", "O+", "Penicillin, Aspirin"),
        ("Mariana Costa", "222.333.444-55", "1992-09-28", "+55 11 97777-2002", "mariana.costa@email.com", "A+", ""),
        ("Lucas Santos", "333.444.555-66", "2001-01-15", "+55 11 97777-2003", "lucas.santos@email.com", "B+", "Sulfa"),
        ("Beatriz Souza", "444.555.666-77", "1978-11-03", "+55 11 97777-2004", "beatriz.souza@email.com", "AB-", ""),
        ("Eduardo Lima", "555.666.777-88", "1965-06-20", "+55 11 97777-2005", "eduardo.lima@email.com", "O-", "Dipyrone"),
    ]
    patients = []
    for p in patients_data:
        pat = pat_service.register_patient(
            name=p[0],
            national_id=p[1],
            birth_date=p[2],
            phone=p[3],
            email=p[4],
            blood_type=p[5],
            allergies=p[6],
        )
        patients.append(pat)

    # 3. Medicines (Pharmacy Catalog)
    medicines_data = [
        ("Amoxicillin", "500mg", "Capsule", 60, 14.50, "2027-12-31", "Amoxicillin", 15),
        ("Paracetamol", "750mg", "Tablet", 150, 4.20, "2028-05-15", "Paracetamol", 20),
        ("Ibuprofen", "400mg", "Tablet", 90, 7.80, "2027-10-10", "Ibuprofen", 15),
        ("Omeprazole", "20mg", "Capsule", 40, 16.00, "2027-08-20", "Omeprazole", 10),
        ("Salbutamol Spray", "100mcg", "Inhaler", 6, 24.50, "2026-11-30", "Salbutamol", 10),  # Low stock!
        ("Losartan Potassium", "50mg", "Tablet", 120, 8.90, "2028-01-20", "Losartan", 25),
        ("Metformin", "850mg", "Tablet", 110, 9.50, "2028-03-10", "Metformin", 20),
        ("Dipyrone Drops", "500mg/ml", "Drops", 4, 5.50, "2027-04-18", "Dipyrone", 10),      # Low stock!
        ("Ceftriaxone", "1g", "Injection", 18, 38.00, "2027-09-01", "Ceftriaxone", 10),
        ("Azithromycin", "500mg", "Tablet", 35, 19.90, "2027-07-25", "Azithromycin", 10),
    ]
    medicines = []
    for m in medicines_data:
        med = pharma_service.add_medicine(
            name=m[0],
            dosage=m[1],
            form=m[2],
            stock_quantity=m[3],
            unit_price=m[4],
            expiration_date=m[5],
            active_ingredient=m[6],
            min_threshold=m[7],
        )
        medicines.append(med)

    # 4. Sample Appointments
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")

    apt1 = apt_service.book_appointment(
        patient_id=patients[0].id,  # Carlos Silva
        doctor_id=doctors[0].id,    # Dr. Watson (Cardiology)
        appointment_date=tomorrow,
        time_slot="09:00",
        notes="Routine cardiovascular checkup, reports mild hypertension.",
    )

    apt2 = apt_service.book_appointment(
        patient_id=patients[1].id,  # Mariana Costa
        doctor_id=doctors[3].id,    # Dr. Sofia (Pediatrics)
        appointment_date=tomorrow,
        time_slot="10:30",
        notes="Child vaccination follow-up.",
    )

    apt3 = apt_service.book_appointment(
        patient_id=patients[3].id,  # Beatriz Souza
        doctor_id=doctors[2].id,    # Dr. House (Internal Medicine)
        appointment_date=day_after,
        time_slot="11:00",
        notes="Chronic abdominal discomfort investigation.",
    )

    # 5. Sample Prescription for ready-to-test dispensing
    # Mariana Costa (no allergies) prescribed Paracetamol and Omeprazole
    rx1 = pharma_service.create_prescription(
        patient_id=patients[1].id,
        doctor_id=doctors[2].id,
        items=[
            {
                "medicine_id": medicines[1].id,  # Paracetamol
                "quantity_prescribed": 2,
                "dosage_instructions": "Take 1 tablet every 8 hours if experiencing fever.",
            },
            {
                "medicine_id": medicines[3].id,  # Omeprazole
                "quantity_prescribed": 1,
                "dosage_instructions": "Take 1 capsule every morning on an empty stomach.",
            },
        ],
        notes="Prescription following general consultation.",
    )

    if not quiet:
        print(f"✅ Successfully seeded:")
        print(f"   - {len(doctors)} Doctors")
        print(f"   - {len(patients)} Patients")
        print(f"   - {len(medicines)} Medicines in Pharmacy Inventory")
        print(f"   - 3 Appointments scheduled for upcoming days")
        print(f"   - 1 Pending Prescription ({rx1.id}) ready for dispensing test")

