"""
Appointment domain model.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import sqlite3


@dataclass
class Appointment:
    id: str
    patient_id: str
    doctor_id: str
    appointment_date: str  # YYYY-MM-DD
    time_slot: str         # HH:MM
    status: str            # SCHEDULED, COMPLETED, CANCELLED
    notes: str = ""
    created_at: Optional[str] = None
    # Joined / enrichment fields for convenience in UI
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None

    @property
    def is_active(self) -> bool:
        return self.status == "SCHEDULED"

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Appointment":
        keys = row.keys()
        return cls(
            id=row["id"],
            patient_id=row["patient_id"],
            doctor_id=row["doctor_id"],
            appointment_date=row["appointment_date"],
            time_slot=row["time_slot"],
            status=row["status"],
            notes=row["notes"] or "",
            created_at=row["created_at"] if "created_at" in keys else None,
            patient_name=row["patient_name"] if "patient_name" in keys else None,
            doctor_name=row["doctor_name"] if "doctor_name" in keys else None,
            specialty=row["specialty"] if "specialty" in keys else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor_name,
            "specialty": self.specialty,
            "appointment_date": self.appointment_date,
            "time_slot": self.time_slot,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at,
        }

