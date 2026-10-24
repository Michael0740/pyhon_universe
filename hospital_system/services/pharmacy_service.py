"""
Pharmacy service layer: Manages medicine inventory, prescription authoring,
allergy cross-checking, and atomic medicine dispensing.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import (
    ValidationError,
    MedicineNotFoundError,
    PatientNotFoundError,
    DoctorNotFoundError,
    PrescriptionNotFoundError,
    InsufficientStockError,
    ExpiredMedicineError,
    PrescriptionAlreadyDispensedError,
)
from hospital_system.models.medicine import Medicine
from hospital_system.models.prescription import Prescription, PrescriptionItem, DispenseRecord
from hospital_system.models.patient import Patient


class PharmacyService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _generate_med_id(self) -> str:
        return self.db.get_next_id("medicines", "MED")

    def _generate_rx_id(self) -> str:
        return self.db.get_next_id("prescriptions", "RX")

    def _generate_dsp_id(self, conn: Optional[Any] = None) -> str:
        return self.db.get_next_id("dispense_records", "DSP", conn=conn)

    # -------------------------------------------------------------
    # MEDICINE INVENTORY MANAGEMENT
    # -------------------------------------------------------------

    def add_medicine(
        self,
        name: str,
        dosage: str,
        form: str,
        stock_quantity: int,
        unit_price: float,
        expiration_date: str,
        active_ingredient: Optional[str] = None,
        min_threshold: int = 10,
    ) -> Medicine:
        """Adds a new medicine to pharmacy inventory with safety validations."""
        clean_name = name.strip()
        clean_dosage = dosage.strip()
        clean_form = form.strip().capitalize()
        clean_ai = active_ingredient.strip() if active_ingredient else None
        clean_exp = expiration_date.strip()

        if not clean_name:
            raise ValidationError("Medicine name cannot be empty.")
        if not clean_dosage:
            raise ValidationError("Medicine dosage cannot be empty (e.g. '500mg').")
        if not clean_form:
            raise ValidationError("Dosage form cannot be empty (e.g. 'Tablet', 'Syrup').")
        if stock_quantity < 0:
            raise ValidationError("Stock quantity cannot be negative.")
        if min_threshold < 0:
            raise ValidationError("Minimum threshold cannot be negative.")
        if unit_price < 0.0:
            raise ValidationError("Unit price cannot be negative.")

        try:
            exp_d = datetime.strptime(clean_exp, "%Y-%m-%d").date()
            if exp_d <= date.today():
                raise ValidationError(f"Cannot add medicine with expired date ({clean_exp}).")
        except ValueError:
            raise ValidationError("Expiration date must be in YYYY-MM-DD format.")

        med_id = self._generate_med_id()
        query = """
        INSERT INTO medicines (id, name, active_ingredient, dosage, form, stock_quantity, min_threshold, unit_price, expiration_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(
            query,
            (med_id, clean_name, clean_ai, clean_dosage, clean_form, stock_quantity, min_threshold, float(unit_price), clean_exp),
        )
        return self.get_medicine(med_id)

    def get_medicine(self, medicine_id: str) -> Medicine:
        """Retrieves a medicine by ID or raises MedicineNotFoundError."""
        row = self.db.fetch_one("SELECT * FROM medicines WHERE id = ?", (medicine_id.strip(),))
        if not row:
            raise MedicineNotFoundError(f"Medicine with ID '{medicine_id}' was not found.")
        return Medicine.from_row(row)

    def restock_medicine(self, medicine_id: str, quantity: int) -> Medicine:
        """Safely increments stock quantity for a medicine."""
        if quantity <= 0:
            raise ValidationError("Restock quantity must be a positive integer greater than zero.")

        med = self.get_medicine(medicine_id)
        new_stock = med.stock_quantity + quantity
        self.db.execute(
            "UPDATE medicines SET stock_quantity = ? WHERE id = ?",
            (new_stock, med.id),
        )
        return self.get_medicine(med.id)

    def search_medicines(self, query: str) -> List[Medicine]:
        """Searches medicines by name or active ingredient."""
        q = f"%{query.strip()}%"
        sql = """
        SELECT * FROM medicines 
        WHERE name LIKE ? OR active_ingredient LIKE ?
        ORDER BY name ASC
        """
        rows = self.db.fetch_all(sql, (q, q))
        return [Medicine.from_row(r) for r in rows]

    def list_medicines(self, low_stock_only: bool = False) -> List[Medicine]:
        """Lists medicines in catalog, optionally filtering by low stock status."""
        if low_stock_only:
            sql = "SELECT * FROM medicines WHERE stock_quantity <= min_threshold ORDER BY stock_quantity ASC"
        else:
            sql = "SELECT * FROM medicines ORDER BY name ASC"
        rows = self.db.fetch_all(sql)
        return [Medicine.from_row(r) for r in rows]

    def get_low_stock_medicines(self) -> List[Medicine]:
        """Convenience method returning all medicines currently at or below safety threshold."""
        return self.list_medicines(low_stock_only=True)

    # -------------------------------------------------------------
    # PRESCRIPTION MANAGEMENT & ALLERGY SAFETY
    # -------------------------------------------------------------

    def create_prescription(
        self,
        patient_id: str,
        doctor_id: str,
        items: List[Dict[str, Any]],
        appointment_id: Optional[str] = None,
        notes: str = "",
        bypass_allergy_warning: bool = False,
    ) -> Prescription:
        """
        Creates a new prescription.
        Includes an automatic safety cross-check of patient allergies against prescribed medicines!
        """
        # Validate patient
        p_row = self.db.fetch_one("SELECT * FROM patients WHERE id = ?", (patient_id.strip(),))
        if not p_row:
            raise PatientNotFoundError(f"Patient with ID '{patient_id}' not found.")
        patient = Patient.from_row(p_row)

        # Validate doctor
        d_row = self.db.fetch_one("SELECT * FROM doctors WHERE id = ?", (doctor_id.strip(),))
        if not d_row:
            raise DoctorNotFoundError(f"Doctor with ID '{doctor_id}' not found.")

        # Validate appointment if provided
        if appointment_id:
            apt_row = self.db.fetch_one("SELECT id FROM appointments WHERE id = ?", (appointment_id.strip(),))
            if not apt_row:
                raise ValidationError(f"Appointment ID '{appointment_id}' does not exist.")

        if not items:
            raise ValidationError("A prescription must contain at least one medicine item.")

        # Pre-validate all items and check allergies
        validated_items = []
        allergy_alerts = []

        for item in items:
            med_id = str(item.get("medicine_id", "")).strip()
            qty = int(item.get("quantity_prescribed", 0))
            instructions = str(item.get("dosage_instructions", "")).strip()

            if not med_id:
                raise ValidationError("Each prescription item must specify a medicine ID.")
            if qty <= 0:
                raise ValidationError(f"Prescribed quantity for medicine '{med_id}' must be greater than zero.")
            if not instructions:
                raise ValidationError(f"Dosage instructions are required for medicine '{med_id}'.")

            med = self.get_medicine(med_id)

            # Allergy check
            if patient.allergies:
                if patient.is_allergic_to(med.name):
                    allergy_alerts.append(f"Patient is allergic to '{med.name}' (allergies: {patient.allergies})")
                if med.active_ingredient and patient.is_allergic_to(med.active_ingredient):
                    allergy_alerts.append(
                        f"Patient is allergic to active ingredient '{med.active_ingredient}' in '{med.name}' (allergies: {patient.allergies})"
                    )

            validated_items.append((med, qty, instructions))

        if allergy_alerts and not bypass_allergy_warning:
            raise ValidationError(
                "CRITICAL ALLERGY WARNING:\n" + "\n".join(allergy_alerts) + 
                "\nPlease choose an alternative medication."
            )

        rx_id = self._generate_rx_id()

        # Save prescription and items atomically
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO prescriptions (id, patient_id, doctor_id, appointment_id, notes, status)
                VALUES (?, ?, ?, ?, ?, 'PENDING')
                """,
                (rx_id, patient.id, doctor_id.strip(), appointment_id.strip() if appointment_id else None, notes.strip()),
            )

            for med, qty, instructions in validated_items:
                conn.execute(
                    """
                    INSERT INTO prescription_items (prescription_id, medicine_id, dosage_instructions, quantity_prescribed, quantity_dispensed)
                    VALUES (?, ?, ?, ?, 0)
                    """,
                    (rx_id, med.id, instructions, qty),
                )

        return self.get_prescription(rx_id)

    def get_prescription(self, prescription_id: str) -> Prescription:
        """Retrieves a prescription with its joined items and names."""
        query = """
        SELECT rx.*, 
               p.name AS patient_name, 
               d.name AS doctor_name
        FROM prescriptions rx
        JOIN patients p ON rx.patient_id = p.id
        JOIN doctors d ON rx.doctor_id = d.id
        WHERE rx.id = ?
        """
        row = self.db.fetch_one(query, (prescription_id.strip(),))
        if not row:
            raise PrescriptionNotFoundError(f"Prescription with ID '{prescription_id}' was not found.")

        prescription = Prescription.from_row(row)

        item_rows = self.db.fetch_all(
            """
            SELECT pi.*, m.name AS medicine_name, m.dosage, m.form
            FROM prescription_items pi
            JOIN medicines m ON pi.medicine_id = m.id
            WHERE pi.prescription_id = ?
            """,
            (prescription.id,),
        )
        prescription.items = [PrescriptionItem.from_row(r) for r in item_rows]
        return prescription

    def list_prescriptions(
        self,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Prescription]:
        """Lists prescriptions with optional patient or status filters."""
        conditions = []
        params = []

        if patient_id:
            conditions.append("rx.patient_id = ?")
            params.append(patient_id.strip())
        if status:
            conditions.append("rx.status = ?")
            params.append(status.strip().upper())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
        SELECT rx.*, 
               p.name AS patient_name, 
               d.name AS doctor_name
        FROM prescriptions rx
        JOIN patients p ON rx.patient_id = p.id
        JOIN doctors d ON rx.doctor_id = d.id
        {where_clause}
        ORDER BY rx.created_at DESC
        """
        rows = self.db.fetch_all(query, tuple(params))
        result = []
        for r in rows:
            rx = Prescription.from_row(r)
            # Load items
            item_rows = self.db.fetch_all(
                """
                SELECT pi.*, m.name AS medicine_name, m.dosage, m.form
                FROM prescription_items pi
                JOIN medicines m ON pi.medicine_id = m.id
                WHERE pi.prescription_id = ?
                """,
                (rx.id,),
            )
            rx.items = [PrescriptionItem.from_row(ir) for ir in item_rows]
            result.append(rx)
        return result

    # -------------------------------------------------------------
    # MEDICINE DISPENSING (PRESCRIPTION & DIRECT)
    # -------------------------------------------------------------

    def dispense_prescription(
        self,
        prescription_id: str,
        pharmacist_notes: str = "",
    ) -> List[DispenseRecord]:
        """
        Fulfills and dispenses a prescription.
        Atomically validates stock for all items, prevents expiration dispensing,
        decrements stock, and creates audit records.
        """
        rx = self.get_prescription(prescription_id)
        if rx.status == "DISPENSED":
            raise PrescriptionAlreadyDispensedError(f"Prescription '{prescription_id}' has already been dispensed.")
        if rx.status == "CANCELLED":
            raise ValidationError(f"Prescription '{prescription_id}' is cancelled and cannot be dispensed.")

        if not rx.items:
            raise ValidationError("Prescription has no items to dispense.")

        dispense_records: List[DispenseRecord] = []

        # Atomic transaction: verify all stocks first, then decrement and record
        with self.db.transaction() as conn:
            # 1. Validation pass
            for item in rx.items:
                remaining_to_dispense = item.quantity_prescribed - item.quantity_dispensed
                if remaining_to_dispense <= 0:
                    continue

                med_row = conn.execute("SELECT * FROM medicines WHERE id = ?", (item.medicine_id,)).fetchone()
                if not med_row:
                    raise MedicineNotFoundError(f"Medicine with ID '{item.medicine_id}' not found.")
                med = Medicine.from_row(med_row)

                if med.is_expired:
                    raise ExpiredMedicineError(
                        f"Cannot dispense '{med.name}': Expired on {med.expiration_date}."
                    )

                if med.stock_quantity < remaining_to_dispense:
                    raise InsufficientStockError(
                        medicine_name=med.name,
                        requested=remaining_to_dispense,
                        available=med.stock_quantity,
                    )

            # 2. Execution pass
            for item in rx.items:
                remaining_to_dispense = item.quantity_prescribed - item.quantity_dispensed
                if remaining_to_dispense <= 0:
                    continue

                med_row = conn.execute("SELECT * FROM medicines WHERE id = ?", (item.medicine_id,)).fetchone()
                med = Medicine.from_row(med_row)

                total_cost = round(remaining_to_dispense * med.unit_price, 2)
                dsp_id = self._generate_dsp_id(conn=conn)

                # Decrement stock
                conn.execute(
                    "UPDATE medicines SET stock_quantity = stock_quantity - ? WHERE id = ?",
                    (remaining_to_dispense, med.id),
                )

                # Update item dispensed count
                conn.execute(
                    "UPDATE prescription_items SET quantity_dispensed = quantity_prescribed WHERE id = ?",
                    (item.id,),
                )

                # Insert dispense log record
                conn.execute(
                    """
                    INSERT INTO dispense_records (id, prescription_id, patient_id, medicine_id, quantity, unit_price, total_cost, pharmacist_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (dsp_id, rx.id, rx.patient_id, med.id, remaining_to_dispense, med.unit_price, total_cost, pharmacist_notes.strip()),
                )

                dispense_records.append(
                    DispenseRecord(
                        id=dsp_id,
                        prescription_id=rx.id,
                        patient_id=rx.patient_id,
                        medicine_id=med.id,
                        quantity=remaining_to_dispense,
                        unit_price=med.unit_price,
                        total_cost=total_cost,
                        pharmacist_notes=pharmacist_notes.strip(),
                        patient_name=rx.patient_name,
                        medicine_name=med.name,
                    )
                )

            # Mark prescription as fulfilled
            conn.execute("UPDATE prescriptions SET status = 'DISPENSED' WHERE id = ?", (rx.id,))

        return dispense_records

    def dispense_direct(
        self,
        patient_id: str,
        medicine_id: str,
        quantity: int,
        pharmacist_notes: str = "",
        bypass_allergy_warning: bool = False,
    ) -> DispenseRecord:
        """
        Dispenses medicine directly to a patient (OTC / immediate care)
        with stock verification, allergy checks, and transaction logging.
        """
        p_row = self.db.fetch_one("SELECT * FROM patients WHERE id = ?", (patient_id.strip(),))
        if not p_row:
            raise PatientNotFoundError(f"Patient with ID '{patient_id}' not found.")
        patient = Patient.from_row(p_row)

        if quantity <= 0:
            raise ValidationError("Dispense quantity must be greater than zero.")

        med = self.get_medicine(medicine_id)

        # Allergy check
        if not bypass_allergy_warning and patient.allergies:
            if patient.is_allergic_to(med.name) or (med.active_ingredient and patient.is_allergic_to(med.active_ingredient)):
                raise ValidationError(
                    f"ALLERGY WARNING: Patient '{patient.name}' is recorded allergic to '{med.name}' / '{patient.allergies}'."
                )

        if med.is_expired:
            raise ExpiredMedicineError(f"Cannot dispense '{med.name}': Expired on {med.expiration_date}.")

        with self.db.transaction() as conn:
            # Re-read stock under lock
            med_row = conn.execute("SELECT * FROM medicines WHERE id = ?", (med.id,)).fetchone()
            current_med = Medicine.from_row(med_row)

            if current_med.stock_quantity < quantity:
                raise InsufficientStockError(
                    medicine_name=current_med.name,
                    requested=quantity,
                    available=current_med.stock_quantity,
                )

            total_cost = round(quantity * current_med.unit_price, 2)
            dsp_id = self._generate_dsp_id(conn=conn)

            conn.execute(
                "UPDATE medicines SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (quantity, current_med.id),
            )

            conn.execute(
                """
                INSERT INTO dispense_records (id, prescription_id, patient_id, medicine_id, quantity, unit_price, total_cost, pharmacist_notes)
                VALUES (?, NULL, ?, ?, ?, ?, ?, ?)
                """,
                (dsp_id, patient.id, current_med.id, quantity, current_med.unit_price, total_cost, pharmacist_notes.strip()),
            )

        return DispenseRecord(
            id=dsp_id,
            prescription_id=None,
            patient_id=patient.id,
            medicine_id=current_med.id,
            quantity=quantity,
            unit_price=current_med.unit_price,
            total_cost=total_cost,
            pharmacist_notes=pharmacist_notes.strip(),
            patient_name=patient.name,
            medicine_name=current_med.name,
        )

    def get_dispense_history(
        self,
        patient_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[DispenseRecord]:
        """Retrieves audit trail of all dispensed medicines."""
        conditions = []
        params = []

        if patient_id:
            conditions.append("dr.patient_id = ?")
            params.append(patient_id.strip())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
        SELECT dr.*, 
               p.name AS patient_name, 
               m.name AS medicine_name
        FROM dispense_records dr
        JOIN patients p ON dr.patient_id = p.id
        JOIN medicines m ON dr.medicine_id = m.id
        {where_clause}
        ORDER BY dr.dispensed_at DESC
        LIMIT ?
        """
        params.append(limit)
        rows = self.db.fetch_all(query, tuple(params))
        return [DispenseRecord.from_row(r) for r in rows]
