"""
Medicine and Pharmacy inventory models.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date, datetime
import sqlite3


@dataclass
class Medicine:
    id: str
    name: str
    active_ingredient: Optional[str]
    dosage: str          # e.g. "500mg", "10ml"
    form: str            # Tablet, Capsule, Syrup, Injection, Cream
    stock_quantity: int
    min_threshold: int
    unit_price: float
    expiration_date: str  # YYYY-MM-DD
    created_at: Optional[str] = None

    @property
    def is_low_stock(self) -> bool:
        """Flags if stock is at or below the reorder threshold."""
        return self.stock_quantity <= self.min_threshold

    @property
    def is_out_of_stock(self) -> bool:
        """Flags if there are 0 units available."""
        return self.stock_quantity <= 0

    @property
    def is_expired(self) -> bool:
        """Checks if the expiration date is past today's date."""
        try:
            exp = datetime.strptime(self.expiration_date, "%Y-%m-%d").date()
            return exp < date.today()
        except (ValueError, TypeError):
            return False

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Medicine":
        return cls(
            id=row["id"],
            name=row["name"],
            active_ingredient=row["active_ingredient"],
            dosage=row["dosage"],
            form=row["form"],
            stock_quantity=row["stock_quantity"],
            min_threshold=row["min_threshold"],
            unit_price=float(row["unit_price"]),
            expiration_date=row["expiration_date"],
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "active_ingredient": self.active_ingredient,
            "dosage": self.dosage,
            "form": self.form,
            "stock_quantity": self.stock_quantity,
            "min_threshold": self.min_threshold,
            "unit_price": self.unit_price,
            "expiration_date": self.expiration_date,
            "is_low_stock": self.is_low_stock,
            "is_out_of_stock": self.is_out_of_stock,
            "is_expired": self.is_expired,
            "created_at": self.created_at,
        }

