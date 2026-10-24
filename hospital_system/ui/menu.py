"""
Interactive console menus orchestrating hospital operations.
Features graceful input prompts, validation, exception handling, and responsive workflows.
"""

from datetime import date
from typing import Optional
from hospital_system.core.database import DatabaseManager
from hospital_system.core.exceptions import HospitalException
from hospital_system.services.patient_service import PatientService
from hospital_system.services.doctor_service import DoctorService
from hospital_system.services.appointment_service import AppointmentService
from hospital_system.services.pharmacy_service import PharmacyService
from hospital_system.seed_data import seed_hospital_data
from hospital_system.ui.console import (
    console,
    print_banner,
    print_success,
    print_error,
    print_warning,
    print_info,
    prompt_string,
    prompt_int,
    prompt_float,
    prompt_confirm,
)
from hospital_system.ui.views import (
    display_patients,
    display_patient_card,
    display_doctors,
    display_slots,
    display_appointments,
    display_medicines,
    display_prescription,
    display_dispense_receipt,
    display_dashboard,
)


class HospitalApp:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.patient_svc = PatientService(db)
        self.doctor_svc = DoctorService(db)
        self.appointment_svc = AppointmentService(db)
        self.pharmacy_svc = PharmacyService(db)

    def run(self) -> None:
        """Main application execution loop."""
        while True:
            console.print()
            print_banner("🏥 HOSPITAL CARE MANAGEMENT SYSTEM", "Reliable & Integrated Patient, Appointment & Pharmacy Services")
            console.print("[bold cyan]1.[/bold cyan] 👤 Patient Services (Register, Search, View)")
            console.print("[bold magenta]2.[/bold magenta] 🩺 Doctor Staff (Register, Specialties, Schedules)")
            console.print("[bold blue]3.[/bold blue] 📅 Appointment Scheduling (Book, Calendar, Complete, Cancel)")
            console.print("[bold green]4.[/bold green] 💊 Pharmacy & Medicine Services (Dispense, Stock, Prescriptions)")
            console.print("[bold yellow]5.[/bold yellow] 📊 Hospital Dashboard (Overview & Low Stock Alerts)")
            console.print("[bold white]6.[/bold white] 🌱 Load Realistic Demo Data")
            console.print("[bold red]0.[/bold red] 🚪 Exit")
            console.print()

            choice = prompt_string("Choose an option [0-6]", default="5")
            if choice == "1":
                self.patient_menu()
            elif choice == "2":
                self.doctor_menu()
            elif choice == "3":
                self.appointment_menu()
            elif choice == "4":
                self.pharmacy_menu()
            elif choice == "5":
                self.show_dashboard()
            elif choice == "6":
                seed_hospital_data(self.db)
            elif choice == "0":
                print_info("Thank you for using Hospital Care Management System. Goodbye!")
                break
            else:
                print_error("Invalid selection. Please choose a valid number.")

    # =========================================================================
    # 1. PATIENT MENU
    # =========================================================================

    def patient_menu(self) -> None:
        while True:
            console.print()
            print_banner("👤 PATIENT SERVICES", "Patient records, allergies & contact info")
            console.print("1. ➕ Register New Patient")
            console.print("2. 🔍 Search Patients (by Name, ID, or Phone)")
            console.print("3. 📋 List All Registered Patients")
            console.print("4. ✏ Update Patient Contact Info or Allergies")
            console.print("0. ⬅ Back to Main Menu")
            console.print()

            opt = prompt_string("Select option", default="3")
            if opt == "1":
                self._register_patient()
            elif opt == "2":
                self._search_patients()
            elif opt == "3":
                patients = self.patient_svc.list_patients()
                display_patients(patients)
            elif opt == "4":
                self._update_patient()
            elif opt == "0":
                break

    def _register_patient(self) -> None:
        console.print("\n[bold cyan]--- Register New Patient ---[/bold cyan]")
        try:
            name = prompt_string("Patient Full Name")
            national_id = prompt_string("National ID / CPF (e.g. 123.456.789-00)")
            birth_date = prompt_string("Birth Date (YYYY-MM-DD)")
            phone = prompt_string("Phone Number (e.g. +55 11 98888-7777)")
            email = prompt_string("Email Address (Optional)", allow_empty=True)
            blood_type = prompt_string("Blood Type (A+, A-, B+, B-, AB+, AB-, O+, O-, or leave empty)", allow_empty=True)
            allergies = prompt_string("Known Allergies (Comma separated, e.g. Penicillin, Aspirin or leave empty)", allow_empty=True)

            patient = self.patient_svc.register_patient(
                name=name,
                national_id=national_id,
                birth_date=birth_date,
                phone=phone,
                email=email if email else None,
                blood_type=blood_type if blood_type else None,
                allergies=allergies,
            )
            print_success(f"Patient registered successfully! Assigned ID: [bold yellow]{patient.id}[/bold yellow]")
            display_patient_card(patient)
        except HospitalException as e:
            print_error(str(e))

    def _search_patients(self) -> None:
        query = prompt_string("Enter name, national ID, or phone to search")
        results = self.patient_svc.search_patients(query)
        display_patients(results)

    def _update_patient(self) -> None:
        patient_id = prompt_string("Enter Patient ID to update (e.g. PAT-0001)")
        try:
            patient = self.patient_svc.get_patient(patient_id)
            display_patient_card(patient)

            console.print("\n[dim]Press Enter without typing to keep current value.[/dim]")
            new_phone = prompt_string(f"New Phone [{patient.phone}]", default=patient.phone)
            new_email = prompt_string(f"New Email [{patient.email or 'N/A'}]", default=patient.email or "", allow_empty=True)
            new_allergies = prompt_string(f"Allergies [{patient.allergies or 'None'}]", default=patient.allergies or "", allow_empty=True)

            updated = self.patient_svc.update_patient(
                patient_id=patient.id,
                phone=new_phone,
                email=new_email if new_email else None,
                allergies=new_allergies,
            )
            print_success("Patient record updated successfully!")
            display_patient_card(updated)
        except HospitalException as e:
            print_error(str(e))

    # =========================================================================
    # 2. DOCTOR MENU
    # =========================================================================

    def doctor_menu(self) -> None:
        while True:
            console.print()
            print_banner("🩺 DOCTOR & MEDICAL STAFF SERVICES", "Medical specialists and schedules")
            console.print("1. 📋 List All Doctors")
            console.print("2. 🩺 Filter Doctors by Specialty")
            console.print("3. ⏰ Check Doctor Available Slots for a Date")
            console.print("4. ➕ Register New Doctor")
            console.print("0. ⬅ Back to Main Menu")
            console.print()

            opt = prompt_string("Select option", default="1")
            if opt == "1":
                doctors = self.doctor_svc.list_doctors()
                display_doctors(doctors)
            elif opt == "2":
                specs = self.doctor_svc.list_specialties()
                if specs:
                    console.print(f"[cyan]Available Specialties:[/cyan] {', '.join(specs)}")
                spec = prompt_string("Enter specialty name to filter")
                doctors = self.doctor_svc.list_doctors(specialty=spec)
                display_doctors(doctors)
            elif opt == "3":
                self._check_doctor_slots()
            elif opt == "4":
                self._register_doctor()
            elif opt == "0":
                break

    def _register_doctor(self) -> None:
        console.print("\n[bold magenta]--- Register Medical Doctor ---[/bold magenta]")
        try:
            name = prompt_string("Doctor Full Name (e.g. Dr. Jane Smith)")
            license_num = prompt_string("License / Board Number (e.g. CRM-99482)")
            specialty = prompt_string("Specialty (e.g. Cardiology, Pediatrics, General Medicine)")
            phone = prompt_string("Contact Phone")
            email = prompt_string("Email Address (Optional)", allow_empty=True)
            start_time = prompt_string("Working Hours Start (HH:MM)", default="08:00")
            end_time = prompt_string("Working Hours End (HH:MM)", default="17:00")

            doctor = self.doctor_svc.register_doctor(
                name=name,
                license_number=license_num,
                specialty=specialty,
                phone=phone,
                email=email if email else None,
                start_time=start_time,
                end_time=end_time,
            )
            print_success(f"Doctor registered successfully! Assigned ID: [bold yellow]{doctor.id}[/bold yellow]")
        except HospitalException as e:
            print_error(str(e))

    def _check_doctor_slots(self) -> None:
        doc_id = prompt_string("Enter Doctor ID (e.g. DOC-0001)")
        try:
            doctor = self.doctor_svc.get_doctor(doc_id)
            target_date = prompt_string("Enter Date (YYYY-MM-DD)", default=date.today().strftime("%Y-%m-%d"))
            slots = self.doctor_svc.get_available_slots(doctor.id, target_date)
            display_slots(doctor, target_date, slots)
        except HospitalException as e:
            print_error(str(e))

    # =========================================================================
    # 3. APPOINTMENT MENU
    # =========================================================================

    def appointment_menu(self) -> None:
        while True:
            console.print()
            print_banner("📅 APPOINTMENT SERVICES", "Booking, calendar, and consultation notes")
            console.print("1. ➕ Book an Appointment")
            console.print("2. 📋 View All Scheduled Appointments")
            console.print("3. 🔍 Filter Appointments (by Date or Doctor)")
            console.print("4. ✅ Complete Appointment & Add Clinical Notes")
            console.print("5. 🔄 Reschedule Appointment")
            console.print("6. ✖ Cancel Appointment")
            console.print("0. ⬅ Back to Main Menu")
            console.print()

            opt = prompt_string("Select option", default="2")
            if opt == "1":
                self._book_appointment()
            elif opt == "2":
                appointments = self.appointment_svc.list_appointments()
                display_appointments(appointments)
            elif opt == "3":
                self._filter_appointments()
            elif opt == "4":
                self._complete_appointment()
            elif opt == "5":
                self._reschedule_appointment()
            elif opt == "6":
                self._cancel_appointment()
            elif opt == "0":
                break

    def _book_appointment(self) -> None:
        console.print("\n[bold blue]--- Book Patient Appointment ---[/bold blue]")
        try:
            # 1. Patient
            pat_id = prompt_string("Patient ID (or type 'search' to find)")
            if pat_id.lower() == "search":
                q = prompt_string("Search patient")
                found = self.patient_svc.search_patients(q)
                display_patients(found)
                if not found:
                    return
                pat_id = prompt_string("Enter Patient ID from above")

            patient = self.patient_svc.get_patient(pat_id)
            console.print(f"Selected Patient: [bold white]{patient.name}[/bold white]")

            # 2. Doctor
            doc_id = prompt_string("Doctor ID (or type 'list' to view doctors)")
            if doc_id.lower() == "list":
                display_doctors(self.doctor_svc.list_doctors())
                doc_id = prompt_string("Enter Doctor ID from above")

            doctor = self.doctor_svc.get_doctor(doc_id)
            console.print(f"Selected Doctor: [bold cyan]{doctor.name}[/bold cyan] ({doctor.specialty})")

            # 3. Date & Slot
            apt_date = prompt_string("Appointment Date (YYYY-MM-DD)")
            slots = self.doctor_svc.get_available_slots(doctor.id, apt_date)
            display_slots(doctor, apt_date, slots)
            if not slots:
                print_error("No slots available for this doctor on the selected date.")
                return

            time_slot = prompt_string("Choose Time Slot (HH:MM from above)")
            notes = prompt_string("Appointment Purpose / Reason (Optional)", allow_empty=True)

            appointment = self.appointment_svc.book_appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=apt_date,
                time_slot=time_slot,
                notes=notes,
            )
            print_success(f"Appointment successfully confirmed! ID: [bold yellow]{appointment.id}[/bold yellow]")
            display_appointments([appointment])
        except HospitalException as e:
            print_error(str(e))

    def _filter_appointments(self) -> None:
        filter_date = prompt_string("Filter by Date (YYYY-MM-DD or leave empty)", allow_empty=True)
        doc_id = prompt_string("Filter by Doctor ID (or leave empty)", allow_empty=True)
        results = self.appointment_svc.list_appointments(
            appointment_date=filter_date if filter_date else None,
            doctor_id=doc_id if doc_id else None,
        )
        display_appointments(results)

    def _complete_appointment(self) -> None:
        apt_id = prompt_string("Enter Appointment ID to complete (e.g. APT-0001)")
        try:
            apt = self.appointment_svc.get_appointment(apt_id)
            display_appointments([apt])
            notes = prompt_string("Enter Doctor's Clinical Findings & Consultation Notes")
            completed = self.appointment_svc.complete_appointment(apt_id, consultation_notes=notes)
            print_success(f"Appointment '{apt_id}' completed!")

            # Offer to immediately write a prescription for the patient
            if prompt_confirm("Would you like to write a medicine prescription for this patient now?"):
                self._create_prescription_flow(
                    patient_id=completed.patient_id,
                    doctor_id=completed.doctor_id,
                    appointment_id=completed.id,
                )
        except HospitalException as e:
            print_error(str(e))

    def _reschedule_appointment(self) -> None:
        apt_id = prompt_string("Enter Appointment ID to reschedule")
        try:
            apt = self.appointment_svc.get_appointment(apt_id)
            display_appointments([apt])

            new_date = prompt_string("New Date (YYYY-MM-DD)")
            slots = self.doctor_svc.get_available_slots(apt.doctor_id, new_date)
            doctor = self.doctor_svc.get_doctor(apt.doctor_id)
            display_slots(doctor, new_date, slots)

            new_time = prompt_string("New Time Slot (HH:MM)")
            updated = self.appointment_svc.reschedule_appointment(apt_id, new_date, new_time)
            print_success(f"Appointment rescheduled to {updated.appointment_date} at {updated.time_slot}!")
        except HospitalException as e:
            print_error(str(e))

    def _cancel_appointment(self) -> None:
        apt_id = prompt_string("Enter Appointment ID to cancel")
        try:
            apt = self.appointment_svc.get_appointment(apt_id)
            display_appointments([apt])
            if prompt_confirm(f"Are you sure you want to cancel appointment {apt_id}?"):
                reason = prompt_string("Cancellation reason", allow_empty=True)
                self.appointment_svc.cancel_appointment(apt_id, reason=reason)
                print_success(f"Appointment {apt_id} has been cancelled.")
        except HospitalException as e:
            print_error(str(e))

    # =========================================================================
    # 4. PHARMACY & MEDICINE MENU
    # =========================================================================

    def pharmacy_menu(self) -> None:
        while True:
            console.print()
            print_banner("💊 PHARMACY & MEDICINE SERVICES", "Inventory control, prescriptions, and atomic dispensing")
            console.print("1. 📦 View Medicine Inventory (Catalog & Stock)")
            console.print("2. 🔍 Search Medicines (by Name or Active Ingredient)")
            console.print("3. ⚠ View Low Stock Alerts")
            console.print("4. 📥 Restock Medicine Inventory")
            console.print("5. ➕ Add New Medicine to Catalog")
            console.print("6. 📝 Create New Prescription (with Allergy Cross-Check)")
            console.print("7. 📋 View Prescriptions (Pending / Dispensed)")
            console.print("8. 💊 Dispense Prescription (Atomic fulfillment & receipt)")
            console.print("9. ⚡ Direct / OTC Medicine Dispense")
            console.print("10. 🧾 View Dispensing Audit Trail")
            console.print("0. ⬅ Back to Main Menu")
            console.print()

            opt = prompt_string("Select option", default="1")
            if opt == "1":
                display_medicines(self.pharmacy_svc.list_medicines())
            elif opt == "2":
                q = prompt_string("Search medicine name or active ingredient")
                display_medicines(self.pharmacy_svc.search_medicines(q))
            elif opt == "3":
                low_stocks = self.pharmacy_svc.get_low_stock_medicines()
                if not low_stocks:
                    print_success("All medicines are currently above minimum safety threshold!")
                else:
                    print_warning(f"Found {len(low_stocks)} medicines at or below reorder threshold:")
                    display_medicines(low_stocks)
            elif opt == "4":
                self._restock_medicine()
            elif opt == "5":
                self._add_medicine()
            elif opt == "6":
                self._create_prescription_flow()
            elif opt == "7":
                self._view_prescriptions()
            elif opt == "8":
                self._dispense_prescription()
            elif opt == "9":
                self._dispense_direct()
            elif opt == "10":
                records = self.pharmacy_svc.get_dispense_history(limit=50)
                display_dispense_receipt(records)
            elif opt == "0":
                break

    def _restock_medicine(self) -> None:
        med_id = prompt_string("Enter Medicine ID to restock (e.g. MED-0001)")
        try:
            med = self.pharmacy_svc.get_medicine(med_id)
            console.print(f"Current stock for [bold white]{med.name} ({med.dosage})[/bold white]: [bold cyan]{med.stock_quantity}[/bold cyan] units.")
            qty = prompt_int("Enter quantity units to add", min_val=1)
            updated = self.pharmacy_svc.restock_medicine(med.id, qty)
            print_success(f"Stock updated! New total: [bold green]{updated.stock_quantity}[/bold green] units.")
        except HospitalException as e:
            print_error(str(e))

    def _add_medicine(self) -> None:
        console.print("\n[bold green]--- Add Medicine to Catalog ---[/bold green]")
        try:
            name = prompt_string("Medicine Brand/Name (e.g. Amoxicillin)")
            dosage = prompt_string("Dosage (e.g. 500mg, 10ml)")
            form = prompt_string("Form (e.g. Tablet, Capsule, Syrup, Drops, Injection)")
            stock = prompt_int("Initial Stock Quantity", min_val=0)
            price = prompt_float("Unit Price ($)", min_val=0.0)
            exp_date = prompt_string("Expiration Date (YYYY-MM-DD)")
            active_ing = prompt_string("Active Ingredient (Optional)", allow_empty=True)
            min_thresh = prompt_int("Minimum Safety Threshold", min_val=0)

            med = self.pharmacy_svc.add_medicine(
                name=name,
                dosage=dosage,
                form=form,
                stock_quantity=stock,
                unit_price=price,
                expiration_date=exp_date,
                active_ingredient=active_ing if active_ing else None,
                min_threshold=min_thresh,
            )
            print_success(f"Medicine added to catalog! ID: [bold yellow]{med.id}[/bold yellow]")
            display_medicines([med])
        except HospitalException as e:
            print_error(str(e))

    def _create_prescription_flow(
        self,
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None,
        appointment_id: Optional[str] = None,
    ) -> None:
        console.print("\n[bold cyan]--- Issue New Prescription ---[/bold cyan]")
        try:
            if not patient_id:
                patient_id = prompt_string("Patient ID (e.g. PAT-0001)")
            patient = self.patient_svc.get_patient(patient_id)
            display_patient_card(patient)

            if not doctor_id:
                doctor_id = prompt_string("Prescribing Doctor ID (e.g. DOC-0001)")
            doctor = self.doctor_svc.get_doctor(doctor_id)

            notes = prompt_string("Clinical Notes / Instructions", allow_empty=True)

            items = []
            while True:
                console.print(f"\n[bold]Prescription Item #{len(items) + 1}:[/bold]")
                med_id = prompt_string("Medicine ID (type 'search' or 'catalog' to inspect)")
                if med_id.lower() in ("search", "catalog"):
                    display_medicines(self.pharmacy_svc.list_medicines())
                    med_id = prompt_string("Enter Medicine ID")

                med = self.pharmacy_svc.get_medicine(med_id)
                console.print(f"Selected: [bold white]{med.name} {med.dosage}[/bold white] (In Stock: {med.stock_quantity})")

                qty = prompt_int("Quantity to prescribe", min_val=1)
                instructions = prompt_string("Dosage instructions (e.g. '1 tablet every 8h after meals for 7 days')")

                items.append({
                    "medicine_id": med.id,
                    "quantity_prescribed": qty,
                    "dosage_instructions": instructions,
                })

                if not prompt_confirm("Add another medicine to this prescription?", default=False):
                    break

            try:
                rx = self.pharmacy_svc.create_prescription(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    items=items,
                    appointment_id=appointment_id,
                    notes=notes,
                )
            except HospitalException as err:
                if "CRITICAL ALLERGY WARNING" in str(err):
                    print_warning(str(err))
                    if prompt_confirm("Do you wish to override this warning with explicit doctor authorization?", default=False):
                        rx = self.pharmacy_svc.create_prescription(
                            patient_id=patient.id,
                            doctor_id=doctor.id,
                            items=items,
                            appointment_id=appointment_id,
                            notes=notes + " [Allergy warning overridden with doctor approval]",
                            bypass_allergy_warning=True,
                        )
                    else:
                        print_info("Prescription cancelled to protect patient health.")
                        return
                else:
                    raise err

            print_success(f"Prescription created successfully! ID: [bold yellow]{rx.id}[/bold yellow]")
            display_prescription(rx)

            if prompt_confirm("Would you like to dispense this prescription immediately?", default=True):
                self._dispense_prescription(rx.id)
        except HospitalException as e:
            print_error(str(e))

    def _view_prescriptions(self) -> None:
        status_filter = prompt_string("Filter status ('PENDING', 'DISPENSED', or leave empty for all)", allow_empty=True)
        rxs = self.pharmacy_svc.list_prescriptions(status=status_filter if status_filter else None)
        if not rxs:
            console.print("[dim]No prescriptions found matching criteria.[/dim]")
            return
        for rx in rxs:
            display_prescription(rx)

    def _dispense_prescription(self, rx_id: Optional[str] = None) -> None:
        if not rx_id:
            rx_id = prompt_string("Enter Prescription ID to dispense (e.g. RX-0001)")
        try:
            rx = self.pharmacy_svc.get_prescription(rx_id)
            display_prescription(rx)

            if rx.status == "DISPENSED":
                print_info(f"Prescription '{rx.id}' has already been fulfilled and dispensed.")
                return

            if prompt_confirm(f"Confirm dispensing prescription {rx.id}?"):
                notes = prompt_string("Pharmacist verification notes", default="Verified and dispensed by pharmacy staff", allow_empty=True)
                records = self.pharmacy_svc.dispense_prescription(rx.id, pharmacist_notes=notes)
                print_success(f"Prescription {rx.id} successfully dispensed!")
                display_dispense_receipt(records)
        except HospitalException as e:
            print_error(str(e))

    def _dispense_direct(self) -> None:
        console.print("\n[bold green]--- Direct / OTC Medicine Dispensing ---[/bold green]")
        try:
            pat_id = prompt_string("Patient ID (e.g. PAT-0001)")
            patient = self.patient_svc.get_patient(pat_id)
            display_patient_card(patient)

            med_id = prompt_string("Medicine ID (e.g. MED-0001)")
            med = self.pharmacy_svc.get_medicine(med_id)
            console.print(f"Medicine: [bold white]{med.name} {med.dosage}[/bold white] | Stock: [bold cyan]{med.stock_quantity}[/bold cyan] units | Price: [bold green]${med.unit_price:.2f}[/bold green]")

            qty = prompt_int("Quantity to dispense", min_val=1)
            notes = prompt_string("Dispense notes (e.g. Over-The-Counter purchase)", default="OTC Direct Sale", allow_empty=True)

            try:
                rec = self.pharmacy_svc.dispense_direct(
                    patient_id=patient.id,
                    medicine_id=med.id,
                    quantity=qty,
                    pharmacist_notes=notes,
                )
            except HospitalException as err:
                if "ALLERGY WARNING" in str(err):
                    print_warning(str(err))
                    if prompt_confirm("Do you wish to bypass allergy warning for this direct sale?", default=False):
                        rec = self.pharmacy_svc.dispense_direct(
                            patient_id=patient.id,
                            medicine_id=med.id,
                            quantity=qty,
                            pharmacist_notes=notes + " [Allergy warning bypassed]",
                            bypass_allergy_warning=True,
                        )
                    else:
                        print_info("Sale cancelled for patient safety.")
                        return
                else:
                    raise err

            display_dispense_receipt([rec])
        except HospitalException as e:
            print_error(str(e))

    # =========================================================================
    # 5. DASHBOARD
    # =========================================================================

    def show_dashboard(self) -> None:
        p_count = len(self.patient_svc.list_patients())
        d_count = len(self.doctor_svc.list_doctors(active_only=True))
        sched_count = len(self.appointment_svc.list_appointments(status="SCHEDULED"))
        med_count = len(self.pharmacy_svc.list_medicines())
        low_stocks = self.pharmacy_svc.get_low_stock_medicines()

        stats = {
            "patients_count": p_count,
            "doctors_count": d_count,
            "scheduled_appointments": sched_count,
            "medicines_count": med_count,
            "low_stock_count": len(low_stocks),
        }

        print_banner("📊 HOSPITAL SERVICE DASHBOARD", "Key health system indicators and immediate alerts")
        display_dashboard(stats)

        if low_stocks:
            console.print("\n[bold yellow]⚠ Immediate Attention: The following medicines are below safety stock threshold:[/bold yellow]")
            display_medicines(low_stocks)
        else:
            console.print("\n[green]✔ Pharmacy inventory is well stocked.[/green]")

