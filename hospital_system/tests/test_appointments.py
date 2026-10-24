"""
Unit and integration tests for DoctorService, AppointmentService, and slot collision detection.
"""

import unittest
from datetime import date, timedelta
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import (
    ValidationError,
    DoctorUnavailableError,
    SlotConflictError,
    AppointmentNotFoundError,
)
from hospital_system.services.patient_service import PatientService
from hospital_system.services.doctor_service import DoctorService
from hospital_system.services.appointment_service import AppointmentService


class TestAppointmentService(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager(":memory:")
        self.patient_svc = PatientService(self.db)
        self.doctor_svc = DoctorService(self.db)
        self.appointment_svc = AppointmentService(self.db)

        # Seed 1 doctor and 2 patients
        self.doctor = self.doctor_svc.register_doctor(
            name="Dr. Gregory House",
            license_number="CRM-12345",
            specialty="Diagnostics",
            phone="+1 555-0900",
            start_time="09:00",
            end_time="12:00",
        )
        self.doctor2 = self.doctor_svc.register_doctor(
            name="Dr. James Wilson",
            license_number="CRM-54321",
            specialty="Oncology",
            phone="+1 555-0901",
            start_time="09:00",
            end_time="17:00",
        )

        self.patient1 = self.patient_svc.register_patient(
            name="John Doe",
            national_id="111.111.111-11",
            birth_date="1980-01-01",
            phone="555-1111",
        )
        self.patient2 = self.patient_svc.register_patient(
            name="Jane Doe",
            national_id="222.222.222-22",
            birth_date="1985-02-02",
            phone="555-2222",
        )

        self.future_date = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")

    def tearDown(self):
        self.db.close()

    def test_calculate_available_slots(self):
        # Working hours 09:00 to 12:00 with 30-min duration:
        # Expected: 09:00, 09:30, 10:00, 10:30, 11:00, 11:30
        slots = self.doctor_svc.get_available_slots(self.doctor.id, self.future_date)
        self.assertEqual(len(slots), 6)
        self.assertIn("09:00", slots)
        self.assertIn("11:30", slots)
        self.assertNotIn("12:00", slots)

        # Book 10:00
        self.appointment_svc.book_appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor.id,
            appointment_date=self.future_date,
            time_slot="10:00",
        )

        # 10:00 should no longer be in available slots
        updated_slots = self.doctor_svc.get_available_slots(self.doctor.id, self.future_date)
        self.assertEqual(len(updated_slots), 5)
        self.assertNotIn("10:00", updated_slots)

    def test_book_appointment_success(self):
        apt = self.appointment_svc.book_appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor.id,
            appointment_date=self.future_date,
            time_slot="09:30",
            notes="Initial consultation",
        )
        self.assertEqual(apt.status, "SCHEDULED")
        self.assertEqual(apt.patient_name, "John Doe")
        self.assertEqual(apt.doctor_name, "Dr. Gregory House")

    def test_book_past_date_raises_validation_error(self):
        past_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError) as ctx:
            self.appointment_svc.book_appointment(
                patient_id=self.patient1.id,
                doctor_id=self.doctor.id,
                appointment_date=past_date,
                time_slot="10:00",
            )
        self.assertIn("Cannot schedule appointments in the past", str(ctx.exception))

    def test_book_outside_working_hours_raises_error(self):
        # Doctor works 09:00 to 12:00
        with self.assertRaises(DoctorUnavailableError):
            self.appointment_svc.book_appointment(
                patient_id=self.patient1.id,
                doctor_id=self.doctor.id,
                appointment_date=self.future_date,
                time_slot="14:00",
            )

    def test_double_booking_doctor_collision(self):
        self.appointment_svc.book_appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor.id,
            appointment_date=self.future_date,
            time_slot="09:00",
        )
        # Attempt to book same doctor at same date and slot with different patient
        with self.assertRaises(SlotConflictError) as ctx:
            self.appointment_svc.book_appointment(
                patient_id=self.patient2.id,
                doctor_id=self.doctor.id,
                appointment_date=self.future_date,
                time_slot="09:00",
            )
        self.assertIn("already has an active appointment", str(ctx.exception))

    def test_patient_simultaneous_appointments_collision(self):
        # Patient 1 books Doctor 1 at 09:30
        self.appointment_svc.book_appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor.id,
            appointment_date=self.future_date,
            time_slot="09:30",
        )
        # Patient 1 attempts to book Doctor 2 at same date and slot
        with self.assertRaises(SlotConflictError) as ctx:
            self.appointment_svc.book_appointment(
                patient_id=self.patient1.id,
                doctor_id=self.doctor2.id,
                appointment_date=self.future_date,
                time_slot="09:30",
            )
        self.assertIn("already has another active appointment", str(ctx.exception))

    def test_complete_and_cancel_appointment(self):
        apt = self.appointment_svc.book_appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor.id,
            appointment_date=self.future_date,
            time_slot="11:00",
        )
        completed = self.appointment_svc.complete_appointment(apt.id, consultation_notes="Patient is healthy.")
        self.assertEqual(completed.status, "COMPLETED")
        self.assertIn("Patient is healthy.", completed.notes)

        # Cannot cancel already completed appointment
        with self.assertRaises(ValidationError):
            self.appointment_svc.cancel_appointment(apt.id)

    def test_reschedule_appointment(self):
        apt = self.appointment_svc.book_appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor.id,
            appointment_date=self.future_date,
            time_slot="09:00",
        )
        rescheduled = self.appointment_svc.reschedule_appointment(
            appointment_id=apt.id,
            new_date=self.future_date,
            new_time="11:30",
        )
        self.assertEqual(rescheduled.time_slot, "11:30")

        # Original slot 09:00 should now be freed
        free_slots = self.doctor_svc.get_available_slots(self.doctor.id, self.future_date)
        self.assertIn("09:00", free_slots)
        self.assertNotIn("11:30", free_slots)


if __name__ == "__main__":
    unittest.main()

