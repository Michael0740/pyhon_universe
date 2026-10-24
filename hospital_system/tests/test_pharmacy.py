"""
Unit and integration tests for PharmacyService, inventory control, allergy cross-checks, and atomic dispensing.
"""

import unittest
from datetime import date, timedelta
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import (
    ValidationError,
    InsufficientStockError,
    ExpiredMedicineError,
    PrescriptionAlreadyDispensedError,
)
from hospital_system.services.patient_service import PatientService
from hospital_system.services.doctor_service import DoctorService
from hospital_system.services.pharmacy_service import PharmacyService


class TestPharmacyService(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager(":memory:")
        self.patient_svc = PatientService(self.db)
        self.doctor_svc = DoctorService(self.db)
        self.pharmacy_svc = PharmacyService(self.db)

        self.doctor = self.doctor_svc.register_doctor(
            name="Dr. Lisa Cuddy",
            license_number="CRM-88192",
            specialty="Internal Medicine",
            phone="555-4000",
        )
        self.patient_allergic = self.patient_svc.register_patient(
            name="Allergic Patient",
            national_id="999.111.222-33",
            birth_date="1992-03-10",
            phone="555-4001",
            allergies="Amoxicillin, Penicillin",
        )
        self.patient_healthy = self.patient_svc.register_patient(
            name="Healthy Patient",
            national_id="999.111.222-44",
            birth_date="1995-07-20",
            phone="555-4002",
            allergies="",
        )

        future_exp = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")

        self.amoxicillin = self.pharmacy_svc.add_medicine(
            name="Amoxicillin",
            dosage="500mg",
            form="Capsule",
            stock_quantity=10,
            unit_price=15.00,
            expiration_date=future_exp,
            active_ingredient="Amoxicillin",
            min_threshold=5,
        )

        self.paracetamol = self.pharmacy_svc.add_medicine(
            name="Paracetamol",
            dosage="750mg",
            form="Tablet",
            stock_quantity=50,
            unit_price=5.00,
            expiration_date=future_exp,
            active_ingredient="Paracetamol",
            min_threshold=10,
        )

    def tearDown(self):
        self.db.close()

    def test_add_medicine_validation(self):
        # Negative stock
        future_exp = (date.today() + timedelta(days=200)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError):
            self.pharmacy_svc.add_medicine(
                name="Test Med",
                dosage="10mg",
                form="Tablet",
                stock_quantity=-5,
                unit_price=10.0,
                expiration_date=future_exp,
            )

        # Expired date
        past_exp = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError):
            self.pharmacy_svc.add_medicine(
                name="Expired Med",
                dosage="10mg",
                form="Tablet",
                stock_quantity=20,
                unit_price=10.0,
                expiration_date=past_exp,
            )

    def test_restock_medicine(self):
        updated = self.pharmacy_svc.restock_medicine(self.amoxicillin.id, 15)
        self.assertEqual(updated.stock_quantity, 25)

    def test_low_stock_detection(self):
        # amoxicillin has 10 units, min_threshold is 5 (not low yet)
        self.assertFalse(self.amoxicillin.is_low_stock)

        # Direct dispense 6 units -> leaves 4 units (<= 5, low stock!)
        self.pharmacy_svc.dispense_direct(
            patient_id=self.patient_healthy.id,
            medicine_id=self.amoxicillin.id,
            quantity=6,
        )

        low_medicines = self.pharmacy_svc.get_low_stock_medicines()
        low_ids = [m.id for m in low_medicines]
        self.assertIn(self.amoxicillin.id, low_ids)

    def test_allergy_cross_check_blocks_dangerous_prescription(self):
        # Patient is allergic to Amoxicillin
        with self.assertRaises(ValidationError) as ctx:
            self.pharmacy_svc.create_prescription(
                patient_id=self.patient_allergic.id,
                doctor_id=self.doctor.id,
                items=[{
                    "medicine_id": self.amoxicillin.id,
                    "quantity_prescribed": 2,
                    "dosage_instructions": "1 capsule every 8 hours",
                }],
            )
        self.assertIn("CRITICAL ALLERGY WARNING", str(ctx.exception))

    def test_allergy_warning_can_be_explicitly_bypassed_if_authorized(self):
        rx = self.pharmacy_svc.create_prescription(
            patient_id=self.patient_allergic.id,
            doctor_id=self.doctor.id,
            items=[{
                "medicine_id": self.amoxicillin.id,
                "quantity_prescribed": 1,
                "dosage_instructions": "Emergency monitored dose",
            }],
            bypass_allergy_warning=True,
        )
        self.assertEqual(rx.status, "PENDING")

    def test_atomic_prescription_dispensing(self):
        # Create prescription for healthy patient
        rx = self.pharmacy_svc.create_prescription(
            patient_id=self.patient_healthy.id,
            doctor_id=self.doctor.id,
            items=[
                {
                    "medicine_id": self.paracetamol.id,
                    "quantity_prescribed": 4,
                    "dosage_instructions": "Take 1 tablet as needed",
                },
                {
                    "medicine_id": self.amoxicillin.id,
                    "quantity_prescribed": 2,
                    "dosage_instructions": "Take 1 capsule every 12h",
                },
            ],
        )

        initial_paracetamol_stock = self.pharmacy_svc.get_medicine(self.paracetamol.id).stock_quantity
        initial_amox_stock = self.pharmacy_svc.get_medicine(self.amoxicillin.id).stock_quantity

        receipts = self.pharmacy_svc.dispense_prescription(rx.id, pharmacist_notes="All clear")
        self.assertEqual(len(receipts), 2)

        # Check stocks decremented
        new_paracetamol_stock = self.pharmacy_svc.get_medicine(self.paracetamol.id).stock_quantity
        new_amox_stock = self.pharmacy_svc.get_medicine(self.amoxicillin.id).stock_quantity
        self.assertEqual(new_paracetamol_stock, initial_paracetamol_stock - 4)
        self.assertEqual(new_amox_stock, initial_amox_stock - 2)

        # Check prescription status is updated
        updated_rx = self.pharmacy_svc.get_prescription(rx.id)
        self.assertEqual(updated_rx.status, "DISPENSED")

        # Check re-dispensing fails
        with self.assertRaises(PrescriptionAlreadyDispensedError):
            self.pharmacy_svc.dispense_prescription(rx.id)

    def test_insufficient_stock_aborts_and_rolls_back(self):
        # Amoxicillin has 10 units in stock. Request 20 units.
        rx = self.pharmacy_svc.create_prescription(
            patient_id=self.patient_healthy.id,
            doctor_id=self.doctor.id,
            items=[{
                "medicine_id": self.amoxicillin.id,
                "quantity_prescribed": 20,
                "dosage_instructions": "Heavy course",
            }],
        )

        with self.assertRaises(InsufficientStockError) as ctx:
            self.pharmacy_svc.dispense_prescription(rx.id)
        self.assertIn("Insufficient stock", str(ctx.exception))

        # Check stock was NOT decremented (transaction roll back)
        med = self.pharmacy_svc.get_medicine(self.amoxicillin.id)
        self.assertEqual(med.stock_quantity, 10)

        # Prescription should still be PENDING
        rx_check = self.pharmacy_svc.get_prescription(rx.id)
        self.assertEqual(rx_check.status, "PENDING")

    def test_direct_otc_dispensing(self):
        rec = self.pharmacy_svc.dispense_direct(
            patient_id=self.patient_healthy.id,
            medicine_id=self.paracetamol.id,
            quantity=3,
            pharmacist_notes="OTC counter purchase",
        )
        self.assertEqual(rec.quantity, 3)
        self.assertEqual(rec.total_cost, 15.00)  # 3 * 5.00

        history = self.pharmacy_svc.get_dispense_history(patient_id=self.patient_healthy.id)
        self.assertTrue(len(history) >= 1)
        self.assertEqual(history[0].id, rec.id)


if __name__ == "__main__":
    unittest.main()

