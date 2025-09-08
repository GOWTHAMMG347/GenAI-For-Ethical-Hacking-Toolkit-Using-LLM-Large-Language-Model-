import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


def _make_prompt(tool: str, result: dict | str) -> str:
    """
    Generate a context-aware prompt for Gemini depending on the tool.
    """
    if isinstance(result, dict):
        result_text = str(result)
    else:
        result_text = result

    if tool == "nmap":
        return f"""
You are a penetration tester. Analyze this Nmap scan result:

{result_text}

Tasks:
- Identify services and versions running
- Highlight possible vulnerabilities (with CVE references if known)
- Rate risk level (Low/Medium/High/Critical)
- Suggest exploitation tools or methods
"""
    elif tool == "theHarvester":
        return f"""
You are an OSINT expert. Analyze this theHarvester output:

{result_text}

Tasks:
- Identify discovered emails, hosts, or domains
- Highlight potential attack surfaces (e.g., emails → phishing, domains → subdomain takeovers)
- Rate risk level
- Suggest next reconnaissance or exploitation steps
"""
    elif tool == "sublist3r":
        return f"""
You are a subdomain enumeration specialist. Analyze this Sublist3r output:

{result_text}

Tasks:
- Identify interesting or vulnerable-looking subdomains
- Highlight if any may be staging/test environments
- Rate risk level
- Suggest next recon steps (e.g., brute force, takeover checks)
"""
    elif tool == "sql_injection":
        return f"""
You are a web security specialist. Analyze this SQLmap SQL Injection test output:

{result_text}

Tasks:
- Determine if SQL Injection was found
- Highlight vulnerable parameters or endpoints
- Suggest CVEs or known exploits if relevant
- Rate risk level
"""
    elif tool == "subdomain_enum":
        return f"""
You are a reconnaissance expert. Analyze this custom Subdomain Enumeration output:

{result_text}

Tasks:
- Identify useful subdomains
- Highlight any risky infrastructure exposures
- Rate risk level
- Suggest next actions
"""
    elif tool == "overall":
        return f"""
You are a cybersecurity analyst. Here are combined results from multiple recon tools:

{result_text}

Tasks:
- Summarize main security weaknesses
- Identify attack paths (recon → exploitation)
- Provide an overall risk score (Low/Medium/High/Critical)
- Suggest prioritized mitigation recommendations
"""
    else:
        return f"""
Analyze the following scan result:

{result_text}

Tasks:
- Identify risks
- Suggest exploits or mitigations
"""


def analyze_results_with_ai(result: dict | str, tool: str = "generic") -> str:
    """
    Analyze tool results with Gemini AI.
    """
    try:
        prompt = _make_prompt(tool, result)

        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(
            prompt
        )

        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        return "AI analysis unavailable."
    except Exception as e:
        return f"AI Analysis failed: {str(e)}"
