"""
Unit and integration tests for PatientService and Patient model.
"""

import unittest
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import ValidationError, PatientNotFoundError
from hospital_system.services.patient_service import PatientService


class TestPatientService(unittest.TestCase):
    def setUp(self):
        # Use isolated in-memory database for fast, reliable tests
        self.db = DatabaseManager(":memory:")
        self.service = PatientService(self.db)

    def tearDown(self):
        self.db.close()

    def test_register_patient_success(self):
        patient = self.service.register_patient(
            name="Alice Smith",
            national_id="123.456.789-01",
            birth_date="1990-05-15",
            phone="+1 555-0101",
            email="alice@example.com",
            blood_type="O+",
            allergies="Penicillin, Sulfa",
        )
        self.assertEqual(patient.name, "Alice Smith")
        self.assertEqual(patient.national_id, "123.456.789-01")
        self.assertEqual(patient.blood_type, "O+")
        self.assertTrue(patient.age > 0)
        self.assertTrue(patient.is_allergic_to("penicillin"))
        self.assertTrue(patient.is_allergic_to("Sulfa"))
        self.assertFalse(patient.is_allergic_to("Aspirin"))

    def test_register_empty_name_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.service.register_patient(
                name="   ",
                national_id="123.456.789-02",
                birth_date="1995-01-01",
                phone="+1 555-0102",
            )

    def test_register_duplicate_national_id_raises_validation_error(self):
        self.service.register_patient(
            name="First Patient",
            national_id="999.888.777-66",
            birth_date="1980-01-01",
            phone="+1 555-0001",
        )
        with self.assertRaises(ValidationError) as ctx:
            self.service.register_patient(
                name="Second Patient",
                national_id="999.888.777-66",
                birth_date="1985-02-02",
                phone="+1 555-0002",
            )
        self.assertIn("already registered", str(ctx.exception))

    def test_register_future_birth_date_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.service.register_patient(
                name="Time Traveler",
                national_id="000.000.000-00",
                birth_date="2099-01-01",
                phone="+1 555-9999",
            )

    def test_register_invalid_blood_type_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.service.register_patient(
                name="Invalid Blood",
                national_id="111.111.111-11",
                birth_date="1990-01-01",
                phone="+1 555-1111",
                blood_type="XYZ+",
            )

    def test_get_nonexistent_patient_raises_not_found(self):
        with self.assertRaises(PatientNotFoundError):
            self.service.get_patient("PAT-9999")

    def test_search_patients(self):
        self.service.register_patient(
            name="Carlos Santana",
            national_id="111.222.333-01",
            birth_date="1970-01-01",
            phone="+55 11 99999-1111",
        )
        self.service.register_patient(
            name="Carlos Drummond",
            national_id="111.222.333-02",
            birth_date="1975-01-01",
            phone="+55 11 99999-2222",
        )
        self.service.register_patient(
            name="Ana Paula",
            national_id="111.222.333-03",
            birth_date="1980-01-01",
            phone="+55 11 99999-3333",
        )

        results = self.service.search_patients("Carlos")
        self.assertEqual(len(results), 2)

        results_id = self.service.search_patients("333-03")
        self.assertEqual(len(results_id), 1)
        self.assertEqual(results_id[0].name, "Ana Paula")

    def test_update_patient(self):
        patient = self.service.register_patient(
            name="John Doe",
            national_id="555.555.555-55",
            birth_date="1985-06-15",
            phone="123-456",
            allergies="None",
        )
        updated = self.service.update_patient(
            patient_id=patient.id,
            phone="987-654",
            email="john.doe@hospital.com",
            allergies="Peanuts, Codeine",
        )
        self.assertEqual(updated.phone, "987-654")
        self.assertEqual(updated.email, "john.doe@hospital.com")
        self.assertTrue(updated.is_allergic_to("Codeine"))


if __name__ == "__main__":
    unittest.main()

