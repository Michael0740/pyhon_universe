"""
Doctor service layer: Manages doctor registry, specialties, working hours, and availability slot calculation.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import ValidationError, DoctorNotFoundError
from hospital_system.models.doctor import Doctor


class DoctorService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _generate_id(self) -> str:
        return self.db.get_next_id("doctors", "DOC")

    def register_doctor(
        self,
        name: str,
        license_number: str,
        specialty: str,
        phone: str,
        email: Optional[str] = None,
        start_time: str = "08:00",
        end_time: str = "18:00",
    ) -> Doctor:
        """Registers a doctor with working hour validation."""
        clean_name = name.strip()
        clean_license = license_number.strip().upper()
        clean_spec = specialty.strip().title()
        clean_phone = phone.strip()
        clean_email = email.strip() if email else None
        clean_start = start_time.strip()
        clean_end = end_time.strip()

        if not clean_name:
            raise ValidationError("Doctor name cannot be empty.")
        if not clean_license:
            raise ValidationError("License number (e.g. CRM/Medical Board ID) cannot be empty.")
        if not clean_spec:
            raise ValidationError("Specialty cannot be empty.")
        if not clean_phone:
            raise ValidationError("Phone number cannot be empty.")

        # Validate time format
        try:
            t_start = datetime.strptime(clean_start, "%H:%M").time()
            t_end = datetime.strptime(clean_end, "%H:%M").time()
            if t_start >= t_end:
                raise ValidationError("Doctor's start time must be earlier than end time.")
        except ValueError:
            raise ValidationError("Working hours must be in HH:MM format (e.g., '08:00').")

        # Check unique license
        existing = self.db.fetch_one("SELECT id FROM doctors WHERE license_number = ?", (clean_license,))
        if existing:
            raise ValidationError(f"A doctor with License '{clean_license}' already exists (ID: {existing['id']}).")

        doc_id = self._generate_id()
        query = """
        INSERT INTO doctors (id, name, license_number, specialty, phone, email, start_time, end_time, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """
        self.db.execute(
            query,
            (doc_id, clean_name, clean_license, clean_spec, clean_phone, clean_email, clean_start, clean_end),
        )

        return self.get_doctor(doc_id)

    def get_doctor(self, doctor_id: str) -> Doctor:
        """Retrieves a doctor by ID or raises DoctorNotFoundError."""
        row = self.db.fetch_one("SELECT * FROM doctors WHERE id = ?", (doctor_id.strip(),))
        if not row:
            raise DoctorNotFoundError(f"Doctor with ID '{doctor_id}' was not found.")
        return Doctor.from_row(row)

    def list_doctors(self, specialty: Optional[str] = None, active_only: bool = True) -> List[Doctor]:
        """Lists doctors with optional specialty and active status filtering."""
        conditions = []
        params = []

        if active_only:
            conditions.append("is_active = 1")
        if specialty:
            conditions.append("specialty LIKE ?")
            params.append(f"%{specialty.strip()}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM doctors {where_clause} ORDER BY specialty ASC, name ASC"
        rows = self.db.fetch_all(sql, tuple(params))
        return [Doctor.from_row(r) for r in rows]

    def list_specialties(self) -> List[str]:
        """Returns all distinct specialties currently available in the hospital."""
        rows = self.db.fetch_all("SELECT DISTINCT specialty FROM doctors WHERE is_active = 1 ORDER BY specialty ASC")
        return [r["specialty"] for r in rows]

    def get_available_slots(self, doctor_id: str, date_str: str, slot_duration_minutes: int = 30) -> List[str]:
        """
        Calculates all free appointment slots for a doctor on a given date.
        Subtracts already scheduled appointments.
        """
        doctor = self.get_doctor(doctor_id)
        if not doctor.is_active:
            return []

        # Parse date
        try:
            datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Date must be in YYYY-MM-DD format.")

        # Find booked slots
        booked_rows = self.db.fetch_all(
            """
            SELECT time_slot FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND status != 'CANCELLED'
            """,
            (doctor.id, date_str.strip()),
        )
        booked_slots = {r["time_slot"] for r in booked_rows}

        # Generate all possible slots within doctor's working hours
        t_start = datetime.strptime(doctor.start_time, "%H:%M")
        t_end = datetime.strptime(doctor.end_time, "%H:%M")

        current = t_start
        free_slots: List[str] = []

        while current + timedelta(minutes=slot_duration_minutes) <= t_end:
            slot_str = current.strftime("%H:%M")
            if slot_str not in booked_slots:
                free_slots.append(slot_str)
            current += timedelta(minutes=slot_duration_minutes)

        return free_slots
