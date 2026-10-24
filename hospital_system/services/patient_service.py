"""
Patient service layer: Handles patient registration, validation, search, and profile updates.
"""

import re
from datetime import date, datetime
from typing import List, Optional
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import ValidationError, PatientNotFoundError
from hospital_system.models.patient import Patient


VALID_BLOOD_TYPES = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "UNKNOWN"}


class PatientService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _generate_id(self) -> str:
        return self.db.get_next_id("patients", "PAT")

    def register_patient(
        self,
        name: str,
        national_id: str,
        birth_date: str,
        phone: str,
        email: Optional[str] = None,
        blood_type: Optional[str] = None,
        allergies: str = "",
    ) -> Patient:
        """Registers a new patient after rigorous validation."""
        # Clean inputs
        clean_name = name.strip()
        clean_nid = national_id.strip()
        clean_phone = phone.strip()
        clean_email = email.strip() if email else None
        clean_allergies = allergies.strip() if allergies else ""

        if not clean_name:
            raise ValidationError("Patient name cannot be empty.")
        if len(clean_name) < 2:
            raise ValidationError("Patient name must have at least 2 characters.")
        if not clean_nid:
            raise ValidationError("National ID / CPF cannot be empty.")
        if not clean_phone:
            raise ValidationError("Phone number cannot be empty.")

        # Validate birth_date
        try:
            b_date = datetime.strptime(birth_date.strip(), "%Y-%m-%d").date()
            if b_date > date.today():
                raise ValidationError("Birth date cannot be in the future.")
        except ValueError:
            raise ValidationError("Birth date must be in YYYY-MM-DD format.")

        # Check unique national ID
        existing = self.db.fetch_one("SELECT id FROM patients WHERE national_id = ?", (clean_nid,))
        if existing:
            raise ValidationError(f"A patient with National ID '{clean_nid}' is already registered (ID: {existing['id']}).")

        # Validate blood type if provided
        clean_blood = blood_type.strip().upper() if blood_type else None
        if clean_blood and clean_blood not in VALID_BLOOD_TYPES:
            raise ValidationError(f"Invalid blood type '{clean_blood}'. Allowed: {', '.join(sorted(VALID_BLOOD_TYPES))}")

        # Validate email if provided
        if clean_email:
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            if not re.match(email_pattern, clean_email):
                raise ValidationError(f"Invalid email format: '{clean_email}'.")

        patient_id = self._generate_id()

        query = """
        INSERT INTO patients (id, name, national_id, birth_date, phone, email, blood_type, allergies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(
            query,
            (patient_id, clean_name, clean_nid, birth_date.strip(), clean_phone, clean_email, clean_blood, clean_allergies),
        )

        return self.get_patient(patient_id)

    def get_patient(self, patient_id: str) -> Patient:
        """Retrieves a patient by ID or raises PatientNotFoundError."""
        row = self.db.fetch_one("SELECT * FROM patients WHERE id = ?", (patient_id.strip(),))
        if not row:
            raise PatientNotFoundError(f"Patient with ID '{patient_id}' was not found.")
        return Patient.from_row(row)

    def search_patients(self, query: str) -> List[Patient]:
        """Searches patients by name, national ID, or phone number."""
        q = f"%{query.strip()}%"
        sql = """
        SELECT * FROM patients 
        WHERE name LIKE ? OR national_id LIKE ? OR phone LIKE ?
        ORDER BY name ASC
        """
        rows = self.db.fetch_all(sql, (q, q, q))
        return [Patient.from_row(r) for r in rows]

    def list_patients(self, limit: int = 100, offset: int = 0) -> List[Patient]:
        """Lists registered patients ordered by name."""
        rows = self.db.fetch_all(
            "SELECT * FROM patients ORDER BY name ASC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [Patient.from_row(r) for r in rows]

    def update_patient(
        self,
        patient_id: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        allergies: Optional[str] = None,
    ) -> Patient:
        """Updates contact information and allergy records of an existing patient."""
        patient = self.get_patient(patient_id)

        new_phone = phone.strip() if phone is not None else patient.phone
        new_email = email.strip() if email is not None else patient.email
        new_allergies = allergies.strip() if allergies is not None else patient.allergies

        if new_email:
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            if not re.match(email_pattern, new_email):
                raise ValidationError(f"Invalid email format: '{new_email}'.")

        self.db.execute(
            "UPDATE patients SET phone = ?, email = ?, allergies = ? WHERE id = ?",
            (new_phone, new_email, new_allergies, patient_id),
        )
        return self.get_patient(patient_id)
