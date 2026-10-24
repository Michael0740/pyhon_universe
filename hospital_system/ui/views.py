"""
Views and tables for displaying domain data in the terminal.
"""

from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from typing import List, Dict, Any, Optional
from hospital_system.ui.console import console
from hospital_system.models.patient import Patient
from hospital_system.models.doctor import Doctor
from hospital_system.models.appointment import Appointment
from hospital_system.models.medicine import Medicine
from hospital_system.models.prescription import Prescription, DispenseRecord


def display_patients(patients: List[Patient]) -> None:
    """Renders a formatted table of patients."""
    if not patients:
        console.print("[dim italic]No patients found.[/dim italic]")
        return

    table = Table(title="🏥 Registered Patients", header_style="bold cyan", border_style="dim")
    table.add_column("ID", style="bold yellow", width=10)
    table.add_column("Name", style="bold white")
    table.add_column("Age", justify="center", width=6)
    table.add_column("National ID", width=16)
    table.add_column("Phone", width=18)
    table.add_column("Blood", justify="center", width=7)
    table.add_column("Allergies", style="bold red")

    for p in patients:
        allergies_display = p.allergies if p.allergies else "[dim]None[/dim]"
        blood_display = p.blood_type if p.blood_type else "[dim]--[/dim]"
        table.add_row(
            p.id,
            p.name,
            str(p.age),
            p.national_id,
            p.phone,
            blood_display,
            allergies_display,
        )
    console.print(table)


def display_patient_card(p: Patient) -> None:
    """Renders a single patient profile card."""
    allergies_display = f"[bold red]{p.allergies}[/bold red]" if p.allergies else "[green]No known allergies[/green]"
    content = (
        f"[bold white]ID:[/bold white] {p.id}\n"
        f"[bold white]Full Name:[/bold white] {p.name}\n"
        f"[bold white]National ID:[/bold white] {p.national_id}\n"
        f"[bold white]Birth Date:[/bold white] {p.birth_date} ([cyan]{p.age} years old[/cyan])\n"
        f"[bold white]Phone:[/bold white] {p.phone}\n"
        f"[bold white]Email:[/bold white] {p.email or '[dim]N/A[/dim]'}\n"
        f"[bold white]Blood Type:[/bold white] {p.blood_type or '[dim]Unknown[/dim]'}\n"
        f"[bold white]Allergies:[/bold white] {allergies_display}\n"
        f"[bold white]Registered Since:[/bold white] [dim]{p.created_at or 'N/A'}[/dim]"
    )
    console.print(Panel(content, title=f"👤 Patient: {p.name}", border_style="cyan"))


def display_doctors(doctors: List[Doctor]) -> None:
    """Renders a table of doctors and their specialties."""
    if not doctors:
        console.print("[dim italic]No doctors found.[/dim italic]")
        return

    table = Table(title="🩺 Medical Staff & Specialties", header_style="bold magenta", border_style="dim")
    table.add_column("ID", style="bold yellow", width=10)
    table.add_column("Doctor Name", style="bold white")
    table.add_column("Specialty", style="cyan")
    table.add_column("License", width=12)
    table.add_column("Working Hours", justify="center", width=15)
    table.add_column("Phone", width=18)
    table.add_column("Status", justify="center", width=10)

    for d in doctors:
        status_text = "[green]ACTIVE[/green]" if d.is_active else "[red]INACTIVE[/red]"
        hours = f"{d.start_time} - {d.end_time}"
        table.add_row(d.id, d.name, d.specialty, d.license_number, hours, d.phone, status_text)

    console.print(table)


def display_slots(doctor: Doctor, date_str: str, slots: List[str]) -> None:
    """Renders available slots for an appointment booking."""
    title = f"📅 Available Slots for Dr. {doctor.name} ({doctor.specialty}) on {date_str}"
    if not slots:
        console.print(Panel(f"[bold yellow]No available slots remaining for {date_str}.[/bold yellow]", title=title))
        return

    slots_str = "  ".join([rf"[bold green]\[{s}][/bold green]" for s in slots])
    console.print(Panel(slots_str, title=title, border_style="green"))


def display_appointments(appointments: List[Appointment]) -> None:
    """Renders a table of scheduled, completed, and cancelled appointments."""
    if not appointments:
        console.print("[dim italic]No appointments found.[/dim italic]")
        return

    table = Table(title="📅 Appointments Registry", header_style="bold blue", border_style="dim")
    table.add_column("ID", style="bold yellow", width=10)
    table.add_column("Date", justify="center", width=12)
    table.add_column("Time", justify="center", width=8)
    table.add_column("Patient", style="bold white")
    table.add_column("Doctor", style="cyan")
    table.add_column("Specialty", style="dim")
    table.add_column("Status", justify="center", width=12)
    table.add_column("Notes", style="italic")

    for a in appointments:
        if a.status == "SCHEDULED":
            status_badge = "[bold yellow]SCHEDULED[/bold yellow]"
        elif a.status == "COMPLETED":
            status_badge = "[bold green]COMPLETED[/bold green]"
        else:
            status_badge = "[bold red]CANCELLED[/bold red]"

        table.add_row(
            a.id,
            a.appointment_date,
            a.time_slot,
            a.patient_name or a.patient_id,
            a.doctor_name or a.doctor_id,
            a.specialty or "",
            status_badge,
            a.notes[:40] + ("..." if len(a.notes) > 40 else ""),
        )

    console.print(table)


def display_medicines(medicines: List[Medicine]) -> None:
    """Renders pharmacy medicine catalog with visual stock alerts."""
    if not medicines:
        console.print("[dim italic]No medicines found in catalog.[/dim italic]")
        return

    table = Table(title="💊 Pharmacy Medicine Inventory", header_style="bold green", border_style="dim")
    table.add_column("ID", style="bold yellow", width=10)
    table.add_column("Medicine Name", style="bold white")
    table.add_column("Active Ingredient", style="dim")
    table.add_column("Dosage", width=10)
    table.add_column("Form", width=12)
    table.add_column("Stock", justify="right", width=10)
    table.add_column("Min", justify="right", width=6)
    table.add_column("Price ($)", justify="right", width=10)
    table.add_column("Expiration", justify="center", width=12)
    table.add_column("Stock Status", justify="center", width=14)

    for m in medicines:
        if m.is_out_of_stock:
            stock_badge = "[bold red]OUT OF STOCK[/bold red]"
            stock_qty = f"[bold red]{m.stock_quantity}[/bold red]"
        elif m.is_low_stock:
            stock_badge = "[bold yellow]LOW STOCK[/bold yellow]"
            stock_qty = f"[bold yellow]{m.stock_quantity}[/bold yellow]"
        else:
            stock_badge = "[green]IN STOCK[/green]"
            stock_qty = f"[green]{m.stock_quantity}[/green]"

        exp_str = f"[bold red]{m.expiration_date} (EXPIRED)[/bold red]" if m.is_expired else m.expiration_date

        table.add_row(
            m.id,
            m.name,
            m.active_ingredient or "--",
            m.dosage,
            m.form,
            stock_qty,
            str(m.min_threshold),
            f"${m.unit_price:.2f}",
            exp_str,
            stock_badge,
        )

    console.print(table)


def display_prescription(rx: Prescription) -> None:
    """Renders details of a prescription and prescribed items."""
    status_color = "yellow" if rx.status == "PENDING" else ("green" if rx.status == "DISPENSED" else "red")
    header = (
        f"[bold white]Prescription ID:[/bold white] {rx.id}  "
        f"[bold white]Status:[/bold white] [{status_color}]{rx.status}[/{status_color}]\n"
        f"[bold white]Patient:[/bold white] {rx.patient_name or rx.patient_id}\n"
        f"[bold white]Doctor:[/bold white] {rx.doctor_name or rx.doctor_id}\n"
        f"[bold white]Date:[/bold white] {rx.created_at or 'N/A'}\n"
        f"[bold white]Clinical Notes:[/bold white] {rx.notes or 'None'}"
    )
    console.print(Panel(header, title="📝 Prescription Details", border_style="cyan"))

    table = Table(header_style="bold magenta", border_style="dim")
    table.add_column("Medicine", style="bold white")
    table.add_column("Dosage / Form", width=18)
    table.add_column("Quantity Prescribed", justify="center", width=18)
    table.add_column("Quantity Dispensed", justify="center", width=18)
    table.add_column("Instructions", style="italic")

    for item in rx.items:
        dosage_info = f"{item.dosage or ''} ({item.form or ''})".strip()
        disp_style = "green" if item.is_fully_dispensed else "yellow"
        table.add_row(
            item.medicine_name or item.medicine_id,
            dosage_info,
            str(item.quantity_prescribed),
            f"[{disp_style}]{item.quantity_dispensed}[/{disp_style}]",
            item.dosage_instructions,
        )

    console.print(table)


def display_dispense_receipt(records: List[DispenseRecord]) -> None:
    """Renders an itemized receipt for dispensed medicines."""
    if not records:
        return

    table = Table(title="🧾 Pharmacy Dispense Receipt", header_style="bold green", border_style="green")
    table.add_column("Receipt ID", style="dim", width=10)
    table.add_column("Medicine", style="bold white")
    table.add_column("Qty", justify="center", width=6)
    table.add_column("Unit Price", justify="right", width=12)
    table.add_column("Total", justify="right", style="bold green", width=12)

    total_order = 0.0
    patient_name = records[0].patient_name or records[0].patient_id

    for r in records:
        table.add_row(
            r.id,
            r.medicine_name or r.medicine_id,
            str(r.quantity),
            f"${r.unit_price:.2f}",
            f"${r.total_cost:.2f}",
        )
        total_order += r.total_cost

    console.print(table)
    summary = (
        f"[bold white]Patient:[/bold white] {patient_name}\n"
        f"[bold white]Dispensed At:[/bold white] {records[0].dispensed_at or 'Now'}\n"
        f"[bold white]Total Amount:[/bold white] [bold green]${total_order:.2f}[/bold green]"
    )
    console.print(Panel(summary, title="✅ Dispensing Completed Successfully", border_style="green"))


def display_dashboard(stats: Dict[str, Any]) -> None:
    """Renders high-level hospital KPI dashboard cards."""
    p_card = Panel(f"[bold cyan]{stats['patients_count']}[/bold cyan]\nRegistered", title="👤 Patients", border_style="cyan")
    d_card = Panel(f"[bold magenta]{stats['doctors_count']}[/bold magenta]\nActive Staff", title="🩺 Doctors", border_style="magenta")
    a_card = Panel(f"[bold yellow]{stats['scheduled_appointments']}[/bold yellow]\nUpcoming", title="📅 Appointments", border_style="yellow")
    m_card = Panel(f"[bold green]{stats['medicines_count']}[/bold green]\nCatalog Items", title="💊 Medicines", border_style="green")

    alert_style = "bold red" if stats["low_stock_count"] > 0 else "green"
    l_card = Panel(f"[{alert_style}]{stats['low_stock_count']}[/{alert_style}]\nAction Needed", title="⚠ Low Stock Alerts", border_style=alert_style)

    console.print(Columns([p_card, d_card, a_card, m_card, l_card]))
