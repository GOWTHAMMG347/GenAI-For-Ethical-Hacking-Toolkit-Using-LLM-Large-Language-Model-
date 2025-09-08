# parse_nmap.py
import xml.etree.ElementTree as ET

def parse_nmap_output(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        results = []

        for host in root.findall("host"):
            ip = host.find("address").attrib["addr"]
            for port in host.findall(".//port"):
                port_id = port.attrib["portid"]
                state = port.find("state").attrib["state"]
                service = port.find("service").attrib.get("name", "unknown")
                results.append({"ip": ip, "port": port_id, "state": state, "service": service})
        return results
    except Exception as e:
        return {"error": str(e)}
