"""
Appointment service layer: Enforces conflict detection, doctor availability,
booking, rescheduling, cancellation, and consultation completion.
"""

from datetime import date, datetime
from typing import List, Optional
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import (
    ValidationError,
    SlotConflictError,
    DoctorUnavailableError,
    AppointmentNotFoundError,
    PatientNotFoundError,
    DoctorNotFoundError,
)
from hospital_system.models.appointment import Appointment
from hospital_system.models.patient import Patient
from hospital_system.models.doctor import Doctor


class AppointmentService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _generate_id(self) -> str:
        return self.db.get_next_id("appointments", "APT")

    def book_appointment(
        self,
        patient_id: str,
        doctor_id: str,
        appointment_date: str,
        time_slot: str,
        notes: str = "",
    ) -> Appointment:
        """
        Books a new appointment with strict validation for date, doctor availability,
        and schedule conflict prevention.
        """
        # 1. Validate Patient
        p_row = self.db.fetch_one("SELECT * FROM patients WHERE id = ?", (patient_id.strip(),))
        if not p_row:
            raise PatientNotFoundError(f"Patient with ID '{patient_id}' does not exist.")

        # 2. Validate Doctor
        d_row = self.db.fetch_one("SELECT * FROM doctors WHERE id = ?", (doctor_id.strip(),))
        if not d_row:
            raise DoctorNotFoundError(f"Doctor with ID '{doctor_id}' does not exist.")
        doctor = Doctor.from_row(d_row)
        if not doctor.is_active:
            raise ValidationError(f"Doctor '{doctor.name}' is currently inactive.")

        # 3. Validate Date & Time Format
        clean_date = appointment_date.strip()
        clean_time = time_slot.strip()

        try:
            target_date = datetime.strptime(clean_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Appointment date must be in YYYY-MM-DD format.")

        try:
            datetime.strptime(clean_time, "%H:%M")
        except ValueError:
            raise ValidationError("Appointment time slot must be in HH:MM format (e.g. '09:30').")

        # Check date not in past
        if target_date < date.today():
            raise ValidationError(f"Cannot schedule appointments in the past ({clean_date}).")

        # 4. Validate Doctor Working Hours
        if not doctor.is_within_working_hours(clean_time):
            raise DoctorUnavailableError(
                f"Doctor '{doctor.name}' works between {doctor.start_time} and {doctor.end_time}. "
                f"Slot '{clean_time}' is outside working hours."
            )

        # 5. Check Doctor Slot Conflict
        doc_conflict = self.db.fetch_one(
            """
            SELECT id FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND time_slot = ? AND status != 'CANCELLED'
            """,
            (doctor.id, clean_date, clean_time),
        )
        if doc_conflict:
            raise SlotConflictError(
                f"{doctor.name} already has an active appointment at {clean_date} {clean_time} "
                f"(Appointment ID: {doc_conflict['id']})."
            )

        # 6. Check Patient Slot Conflict (patient cannot be in two places at once)
        pat_conflict = self.db.fetch_one(
            """
            SELECT id FROM appointments 
            WHERE patient_id = ? AND appointment_date = ? AND time_slot = ? AND status != 'CANCELLED'
            """,
            (patient_id.strip(), clean_date, clean_time),
        )
        if pat_conflict:
            raise SlotConflictError(
                f"Patient '{p_row['name']}' already has another active appointment at {clean_date} {clean_time} "
                f"(Appointment ID: {pat_conflict['id']})."
            )

        # 7. Insert Appointment
        apt_id = self._generate_id()
        query = """
        INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, time_slot, status, notes)
        VALUES (?, ?, ?, ?, ?, 'SCHEDULED', ?)
        """
        self.db.execute(
            query,
            (apt_id, patient_id.strip(), doctor.id, clean_date, clean_time, notes.strip()),
        )

        return self.get_appointment(apt_id)

    def get_appointment(self, appointment_id: str) -> Appointment:
        """Retrieves an appointment with patient and doctor details joined."""
        query = """
        SELECT a.*, 
               p.name AS patient_name, 
               d.name AS doctor_name, 
               d.specialty AS specialty
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.id = ?
        """
        row = self.db.fetch_one(query, (appointment_id.strip(),))
        if not row:
            raise AppointmentNotFoundError(f"Appointment with ID '{appointment_id}' was not found.")
        return Appointment.from_row(row)

    def cancel_appointment(self, appointment_id: str, reason: str = "") -> Appointment:
        """Cancels an existing appointment."""
        apt = self.get_appointment(appointment_id)
        if apt.status == "CANCELLED":
            raise ValidationError(f"Appointment '{appointment_id}' is already cancelled.")
        if apt.status == "COMPLETED":
            raise ValidationError(f"Cannot cancel appointment '{appointment_id}' because it has already been completed.")

        note_update = (f"{apt.notes}\n[Cancelled]: {reason}").strip() if reason else apt.notes
        self.db.execute(
            "UPDATE appointments SET status = 'CANCELLED', notes = ? WHERE id = ?",
            (note_update, appointment_id),
        )
        return self.get_appointment(appointment_id)

    def complete_appointment(self, appointment_id: str, consultation_notes: str = "") -> Appointment:
        """Marks an appointment as completed with consultation findings."""
        apt = self.get_appointment(appointment_id)
        if apt.status == "COMPLETED":
            raise ValidationError(f"Appointment '{appointment_id}' is already marked as completed.")
        if apt.status == "CANCELLED":
            raise ValidationError(f"Cannot complete a cancelled appointment '{appointment_id}'.")

        note_update = (f"{apt.notes}\n[Consultation]: {consultation_notes}").strip() if consultation_notes else apt.notes
        self.db.execute(
            "UPDATE appointments SET status = 'COMPLETED', notes = ? WHERE id = ?",
            (note_update, appointment_id),
        )
        return self.get_appointment(appointment_id)

    def reschedule_appointment(self, appointment_id: str, new_date: str, new_time: str) -> Appointment:
        """Reschedules an active appointment to a new date and time."""
        apt = self.get_appointment(appointment_id)
        if apt.status != "SCHEDULED":
            raise ValidationError(f"Only 'SCHEDULED' appointments can be rescheduled. Current status: '{apt.status}'.")

        # Temporarily mark current as cancelled to check conflicts cleanly, then update
        self.db.execute("UPDATE appointments SET status = 'CANCELLED' WHERE id = ?", (appointment_id,))
        try:
            # Check availability with book validation logic
            d_row = self.db.fetch_one("SELECT * FROM doctors WHERE id = ?", (apt.doctor_id,))
            doctor = Doctor.from_row(d_row)

            target_date = datetime.strptime(new_date.strip(), "%Y-%m-%d").date()
            if target_date < date.today():
                raise ValidationError("Cannot reschedule appointment to a date in the past.")

            datetime.strptime(new_time.strip(), "%H:%M")

            if not doctor.is_within_working_hours(new_time.strip()):
                raise DoctorUnavailableError(
                    f"Doctor '{doctor.name}' works between {doctor.start_time} and {doctor.end_time}."
                )

            # Check conflicts
            doc_conflict = self.db.fetch_one(
                "SELECT id FROM appointments WHERE doctor_id = ? AND appointment_date = ? AND time_slot = ? AND status != 'CANCELLED'",
                (doctor.id, new_date.strip(), new_time.strip()),
            )
            if doc_conflict:
                raise SlotConflictError(f"Doctor is already booked at {new_date} {new_time}.")

            self.db.execute(
                "UPDATE appointments SET appointment_date = ?, time_slot = ?, status = 'SCHEDULED' WHERE id = ?",
                (new_date.strip(), new_time.strip(), appointment_id),
            )
        except Exception:
            # Restore state if validation failed
            self.db.execute("UPDATE appointments SET status = 'SCHEDULED' WHERE id = ?", (appointment_id,))
            raise

        return self.get_appointment(appointment_id)

    def list_appointments(
        self,
        appointment_date: Optional[str] = None,
        doctor_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Appointment]:
        """Lists appointments with optional multi-criteria filters."""
        conditions = []
        params = []

        if appointment_date:
            conditions.append("a.appointment_date = ?")
            params.append(appointment_date.strip())
        if doctor_id:
            conditions.append("a.doctor_id = ?")
            params.append(doctor_id.strip())
        if patient_id:
            conditions.append("a.patient_id = ?")
            params.append(patient_id.strip())
        if status:
            conditions.append("a.status = ?")
            params.append(status.strip().upper())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
        SELECT a.*, 
               p.name AS patient_name, 
               d.name AS doctor_name, 
               d.specialty AS specialty
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        {where_clause}
        ORDER BY a.appointment_date ASC, a.time_slot ASC
        """
        rows = self.db.fetch_all(query, tuple(params))
        return [Appointment.from_row(r) for r in rows]
