import subprocess
import json
import nmap

def run_nmap_scan(target: str):
    try:
        # Run Nmap with service detection, OS detection, default scripts, faster timing
        command = ["nmap", "-sV", "-O", "-sC", "-T4", target, "-oX", "-"]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        nm = nmap.PortScanner()
        nm.analyse_nmap_xml_scan(result.stdout)

        scan_data = {}
        for host in nm.all_hosts():
            host_data = {
                "state": nm[host].state(),
                "os": [],
                "ports": []
            }

            # ✅ Safely handle OS detection results
            os_matches = nm[host].get("osmatch", [])
            for match in os_matches:
                host_data["os"].append({
                    "name": match.get("name", ""),
                    "accuracy": match.get("accuracy", ""),
                    "line": match.get("line", "")
                })

            # ✅ Ports and services
            for proto in nm[host].all_protocols():
                for port, service in nm[host][proto].items():
                    host_data["ports"].append({
                        "port": port,
                        "state": service.get("state", ""),
                        "name": service.get("name", ""),
                        "product": service.get("product", ""),
                        "version": service.get("version", "")
                    })

            scan_data[host] = host_data

        return scan_data

    except Exception as e:
        return {"error": str(e)}
