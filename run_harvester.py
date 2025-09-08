import subprocess
import sys
import os
import json

def run_harvester_scan(domain: str, timeout: int = 60):
    try:
        harvester_path = os.path.join(os.getcwd(), "theHarvester", "theHarvester.py")
        if not os.path.exists(harvester_path):
            return {"error": "theHarvester not found. Please clone it in the project root."}

        output_file = os.path.join(os.getcwd(), "harvester_output.json")

        # ✅ Only use supported sources for theHarvester 4.9.0
        # Run "python theHarvester.py -h" to see full list on your system.
        sources = "duckduckgo,crtsh,otx,hunter"

        command = [
            sys.executable,
            harvester_path,
            "-d", domain,
            "-b", sources,
            "-f", output_file
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            return {"error": result.stderr.strip() or result.stdout.strip()}

        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    return {
                        "emails": data.get("emails", []),
                        "hosts": data.get("hosts", []),
                        "domains": data.get("domains", [])
                    }
                except Exception:
                    return {"error": "Failed to parse Harvester JSON output"}
        else:
            return {"error": "No JSON output file generated"}

    except subprocess.TimeoutExpired:
        return {"error": f"theHarvester scan timed out after {timeout} seconds"}
    except Exception as e:
        return {"error": str(e)}
