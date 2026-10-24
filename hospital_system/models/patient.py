"""
Patient domain model.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any
import sqlite3


@dataclass
class Patient:
    id: str
    name: str
    national_id: str
    birth_date: str  # YYYY-MM-DD
    phone: str
    email: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: str = ""
    created_at: Optional[str] = None

    @property
    def age(self) -> int:
        """Calculates current age from birth_date."""
        try:
            born = datetime.strptime(self.birth_date, "%Y-%m-%d").date()
            today = date.today()
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except (ValueError, TypeError):
            return 0

    def is_allergic_to(self, substance: str) -> bool:
        """Checks if the patient has a recorded allergy matching substance."""
        if not self.allergies or not substance:
            return False
        clean_substance = substance.strip().lower()
        allergy_list = [a.strip().lower() for a in self.allergies.split(",") if a.strip()]
        return any(clean_substance in a or a in clean_substance for a in allergy_list)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Patient":
        return cls(
            id=row["id"],
            name=row["name"],
            national_id=row["national_id"],
            birth_date=row["birth_date"],
            phone=row["phone"],
            email=row["email"],
            blood_type=row["blood_type"],
            allergies=row["allergies"] or "",
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "national_id": self.national_id,
            "birth_date": self.birth_date,
            "phone": self.phone,
            "email": self.email,
            "blood_type": self.blood_type,
            "allergies": self.allergies,
            "age": self.age,
            "created_at": self.created_at,
        }

