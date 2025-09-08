import subprocess

def run_custom_subdomain_enum(domain: str):
    try:
        command = ["python", "subdomain_enum.py", domain]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        subs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return {"subdomains": subs}
    except Exception as e:
        return {"error": str(e)}
