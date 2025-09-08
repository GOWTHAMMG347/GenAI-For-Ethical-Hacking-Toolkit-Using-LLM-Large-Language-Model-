import subprocess
import sys
import os

def run_sql_injection(domain: str, timeout: int = 90):
    try:
        sqlmap_path = os.path.join(os.getcwd(), "sqlmap", "sqlmap.py")
        if not os.path.exists(sqlmap_path):
            return {"error": "sqlmap not found. Please clone https://github.com/sqlmapproject/sqlmap into the project root."}

        url = f"http://{domain}"
        # Faster execution: limit crawl depth, add threads, skip lengthy banner/tech detection
        command = [
            sys.executable, sqlmap_path,
            "-u", url,
            "--batch",
            "--crawl=1",       # minimal crawl
            "--threads=3",     # add parallelism
            "--smart",         # faster heuristic checks
            "--output-dir=sqlmap_results"
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            return {"error": result.stderr.strip() or result.stdout.strip()}

        findings = [
            line.strip()
            for line in result.stdout.splitlines()
            if any(keyword in line.lower() for keyword in ["sql injection", "parameter", "vulnerable"])
        ]

        # Truncate long stdout so results return faster
        return {
            "output": result.stdout[:1000] + ("..." if len(result.stdout) > 1000 else ""),
            "findings": findings
        }

    except subprocess.TimeoutExpired:
        return {"error": f"sqlmap scan timed out after {timeout} seconds"}
    except Exception as e:
        return {"error": str(e)}
