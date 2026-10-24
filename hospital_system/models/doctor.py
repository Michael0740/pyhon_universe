"""
Doctor domain model.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import sqlite3


@dataclass
class Doctor:
    id: str
    name: str
    license_number: str
    specialty: str
    phone: str
    email: Optional[str] = None
    start_time: str = "08:00"  # HH:MM
    end_time: str = "18:00"    # HH:MM
    is_active: bool = True
    created_at: Optional[str] = None

    def is_within_working_hours(self, time_str: str) -> bool:
        """Verifies if a given time slot falls within the doctor's working hours."""
        try:
            slot_t = datetime.strptime(time_str, "%H:%M").time()
            start_t = datetime.strptime(self.start_time, "%H:%M").time()
            end_t = datetime.strptime(self.end_time, "%H:%M").time()
            return start_t <= slot_t < end_t
        except (ValueError, TypeError):
            return False

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Doctor":
        return cls(
            id=row["id"],
            name=row["name"],
            license_number=row["license_number"],
            specialty=row["specialty"],
            phone=row["phone"],
            email=row["email"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "license_number": self.license_number,
            "specialty": self.specialty,
            "phone": self.phone,
            "email": self.email,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

