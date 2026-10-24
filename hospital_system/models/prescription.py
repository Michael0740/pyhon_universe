"""
Prescription and Dispensing domain models.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import sqlite3


@dataclass
class PrescriptionItem:
    id: Optional[int]
    prescription_id: str
    medicine_id: str
    dosage_instructions: str
    quantity_prescribed: int
    quantity_dispensed: int = 0
    medicine_name: Optional[str] = None
    dosage: Optional[str] = None
    form: Optional[str] = None

    @property
    def is_fully_dispensed(self) -> bool:
        return self.quantity_dispensed >= self.quantity_prescribed

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "PrescriptionItem":
        keys = row.keys()
        return cls(
            id=row["id"],
            prescription_id=row["prescription_id"],
            medicine_id=row["medicine_id"],
            dosage_instructions=row["dosage_instructions"],
            quantity_prescribed=row["quantity_prescribed"],
            quantity_dispensed=row["quantity_dispensed"],
            medicine_name=row["medicine_name"] if "medicine_name" in keys else None,
            dosage=row["dosage"] if "dosage" in keys else None,
            form=row["form"] if "form" in keys else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prescription_id": self.prescription_id,
            "medicine_id": self.medicine_id,
            "medicine_name": self.medicine_name,
            "dosage": self.dosage,
            "form": self.form,
            "dosage_instructions": self.dosage_instructions,
            "quantity_prescribed": self.quantity_prescribed,
            "quantity_dispensed": self.quantity_dispensed,
            "is_fully_dispensed": self.is_fully_dispensed,
        }


@dataclass
class Prescription:
    id: str
    patient_id: str
    doctor_id: str
    appointment_id: Optional[str] = None
    notes: str = ""
    status: str = "PENDING"  # PENDING, DISPENSED, CANCELLED
    created_at: Optional[str] = None
    items: List[PrescriptionItem] = field(default_factory=list)
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Prescription":
        keys = row.keys()
        return cls(
            id=row["id"],
            patient_id=row["patient_id"],
            doctor_id=row["doctor_id"],
            appointment_id=row["appointment_id"] if "appointment_id" in keys else None,
            notes=row["notes"] or "",
            status=row["status"],
            created_at=row["created_at"] if "created_at" in keys else None,
            patient_name=row["patient_name"] if "patient_name" in keys else None,
            doctor_name=row["doctor_name"] if "doctor_name" in keys else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor_name,
            "appointment_id": self.appointment_id,
            "notes": self.notes,
            "status": self.status,
            "created_at": self.created_at,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass
class DispenseRecord:
    id: str
    prescription_id: Optional[str]
    patient_id: str
    medicine_id: str
    quantity: int
    unit_price: float
    total_cost: float
    pharmacist_notes: str = ""
    dispensed_at: Optional[str] = None
    patient_name: Optional[str] = None
    medicine_name: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "DispenseRecord":
        keys = row.keys()
        return cls(
            id=row["id"],
            prescription_id=row["prescription_id"] if "prescription_id" in keys else None,
            patient_id=row["patient_id"],
            medicine_id=row["medicine_id"],
            quantity=row["quantity"],
            unit_price=float(row["unit_price"]),
            total_cost=float(row["total_cost"]),
            pharmacist_notes=row["pharmacist_notes"] or "",
            dispensed_at=row["dispensed_at"] if "dispensed_at" in keys else None,
            patient_name=row["patient_name"] if "patient_name" in keys else None,
            medicine_name=row["medicine_name"] if "medicine_name" in keys else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prescription_id": self.prescription_id,
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "medicine_id": self.medicine_id,
            "medicine_name": self.medicine_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_cost": self.total_cost,
            "pharmacist_notes": self.pharmacist_notes,
            "dispensed_at": self.dispensed_at,
        }

