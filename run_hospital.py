#!/usr/bin/env python3
"""
Convenience launcher for the Hospital Care Management System.
Run with: python3 run_hospital.py
Or from inside hospital_system: python3 hospital_system/main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hospital_system.main import main

if __name__ == "__main__":
    main()

