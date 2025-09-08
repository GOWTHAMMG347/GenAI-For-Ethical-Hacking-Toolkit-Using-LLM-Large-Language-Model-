import subprocess

def run_sqlmap(domain):
    command = ["sqlmap", "-u", f"http://{domain}", "--batch", "--crawl=1"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout
