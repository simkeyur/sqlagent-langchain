#!/usr/bin/env python
"""Run script for the Employee Database Query Application."""

import os
import sys
import subprocess

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(script_dir, 'app')

# Change to app directory
os.chdir(app_dir)

# Get the Python executable from the virtual environment
venv_python = os.path.join(script_dir, '.venv', 'bin', 'python')

# Run the Flask app
try:
    print("Starting Employee Database Query Application...")
    print("📱 Access the app at http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    subprocess.run([venv_python, 'app.py'])
except KeyboardInterrupt:
    print("\n\nServer stopped.")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
