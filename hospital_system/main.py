#!/usr/bin/env python3
"""
Main entry point for the Hospital Care Management System.
Supports interactive mode, automatic demo seeding, database resets, and running tests.
"""

import sys
import os
import argparse
import unittest

# Ensure the root directory is on the python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from hospital_system.core.database import DatabaseManager
from hospital_system.seed_data import seed_hospital_data
from hospital_system.ui.menu import HospitalApp
from hospital_system.ui.console import console, print_info, print_success, print_warning


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hospital Care Management System - Integrated Patient, Appointment & Pharmacy Platform"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=os.path.join(current_dir, "data", "hospital.db"),
        help="Path to SQLite database file (default: hospital_system/data/hospital.db)",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed realistic initial data (doctors, patients, medicine inventory, appointments)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe the database and reinitialize schema from scratch",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the complete automated unit and integration test suite",
    )
    return parser.parse_args()


def run_tests() -> int:
    """Discovers and runs all tests in the tests package."""
    tests_dir = os.path.join(current_dir, "tests")
    print_info(f"Running automated test suite in: {tests_dir}")
    suite = unittest.defaultTestLoader.discover(tests_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def main() -> None:
    args = parse_arguments()

    if args.test:
        sys.exit(run_tests())

    db_path = args.db

    if args.reset:
        if os.path.exists(db_path):
            os.remove(db_path)
            print_warning(f"Existing database at '{db_path}' was removed.")
        print_success("Database schema reset successfully.")

    # Initialize database
    is_new_db = not os.path.exists(db_path) or os.path.getsize(db_path) == 0
    db = DatabaseManager(db_path)

    # If --seed flag passed, or if brand new database, seed with realistic records
    if args.seed or is_new_db:
        print_info("New or requested database detected. Populating with initial medical catalog & staff...")
        seed_hospital_data(db, quiet=False)

    # Launch interactive application
    app = HospitalApp(db)
    app.run()


if __name__ == "__main__":
    main()

