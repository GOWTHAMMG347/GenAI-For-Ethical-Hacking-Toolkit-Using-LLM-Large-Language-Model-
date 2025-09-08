import subprocess
import sys
import os

def run_sublist3r(domain):
    """
    Run Sublist3r for subdomain enumeration.
    Works with local Sublist3r clone in Windows/Linux.
    """
    try:
        # Path to sublist3r.py inside your project folder
        sublist3r_path = os.path.join(os.getcwd(), "Sublist3r", "sublist3r.py")

        # Run with the current Python interpreter
        result = subprocess.run(
            [sys.executable, sublist3r_path, "-d", domain, "-o", "sublist3r_output.txt"],
            capture_output=True,
            text=True,
            check=True
        )

        # Read results
        with open("sublist3r_output.txt", "r") as f:
            subdomains = f.read().splitlines()

        return {"subdomains": subdomains}

    except Exception as e:
        return {"error": str(e)}
