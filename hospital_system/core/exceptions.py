"""
Custom exceptions for the Hospital Care Management System.
Provides domain-specific, clearly typed error conditions with helpful messages.
"""

class HospitalException(Exception):
    """Base exception for all hospital domain errors."""
    pass


class ValidationError(HospitalException):
    """Raised when an entity or input fails validation checks."""
    pass


class EntityNotFoundError(HospitalException):
    """Base exception when an entity is not found."""
    pass


class PatientNotFoundError(EntityNotFoundError):
    """Raised when a patient ID or record is not found."""
    pass


class DoctorNotFoundError(EntityNotFoundError):
    """Raised when a doctor ID or record is not found."""
    pass


class AppointmentNotFoundError(EntityNotFoundError):
    """Raised when an appointment ID or record is not found."""
    pass


class MedicineNotFoundError(EntityNotFoundError):
    """Raised when a medicine ID or record is not found in the pharmacy."""
    pass


class PrescriptionNotFoundError(EntityNotFoundError):
    """Raised when a prescription record is not found."""
    pass


class SlotConflictError(HospitalException):
    """Raised when an appointment slot is already taken by another patient."""
    pass


class DoctorUnavailableError(HospitalException):
    """Raised when a doctor is not scheduled to work at the requested time."""
    pass


class InsufficientStockError(HospitalException):
    """Raised when attempting to dispense more medicine units than available."""
    def __init__(self, medicine_name: str, requested: int, available: int):
        self.medicine_name = medicine_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for '{medicine_name}': requested {requested}, but only {available} available."
        )


class ExpiredMedicineError(HospitalException):
    """Raised when attempting to dispense an expired medicine batch."""
    pass


class PrescriptionAlreadyDispensedError(HospitalException):
    """Raised when attempting to dispense an already fulfilled prescription."""
    pass

