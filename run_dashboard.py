#!/usr/bin/env python3
"""Launch the Streamlit dashboard."""

import subprocess
import sys
import os

def main():
    dashboard_path = os.path.join(os.path.dirname(__file__), "visualization", "dashboard.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", "8501"])

if __name__ == "__main__":
    main()
