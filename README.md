🔐 GenAI Powered Ethical Hacking Toolkit Using LLM(Large Language Model)

An AI-Powered Ethical Hacking Toolkit that integrates classic penetration testing tools (Nmap, theHarvester, Subdomain Enumeration, SQL Injection) with Google Gemini AI for automated analysis and report generation.

📌 Features

✅ Nmap Scanner – Run port scans and parse results
✅ theHarvester Integration – Collect emails, subdomains, and hosts
✅ Subdomain Enumeration – Find hidden assets using Sublist3r & custom scripts
✅ SQL Injection Tester – Basic SQLi vulnerability checks
✅ AI-Powered Analysis – Uses Google Gemini API to analyze results and generate insights
✅ PDF Security Reports – Auto-generate professional security reports

📂 Project Structure
geminiapi/
│── app.py                 # Main entry point (runs scans + reporting)
│── config.py              # Configuration & API key management
│── prompt_handler.py      # Handles Gemini API prompts & responses
│── report_generator.py    # Creates PDF reports
│── parse_nmap.py          # Parse Nmap XML results
│── run_nmap.py            # Run Nmap scans
│── run_harvester.py       # Run theHarvester
│── run_subdomain_enum.py  # Run subdomain enum
│── run_sublist3r.py       # Alternative subdomain scan with Sublist3r
│── run_sql_injection.py   # Run SQL Injection checks
│── sql_injection.py       # SQLi logic
│── subdomain_enum.py      # Subdomain logic
│── requirements.txt       # Python dependencies
│── .env                   # API keys & environment variables
│── *_output.*             # Scan results (XML, JSON, TXT)
│── security_report_*.pdf  # Generated reports

⚙️ Installation
1️⃣ Clone the repository
git clone https://github.com/yourusername/genai-eth-hacking.git
cd genai-eth-hacking/geminiapi

2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure environment

Create a .env file in the geminiapi/ directory:

GEMINI_API_KEY=your_google_gemini_api_key_here

🚀 Usage

You can run each module independently, or orchestrate everything via app.py.

🔎 Run Nmap Scan
python run_nmap.py -t example.com


Output saved as nmap_output.xml.

📧 Run theHarvester
python run_harvester.py -d example.com


Output saved as harvester_output.json.

🌍 Subdomain Enumeration
python run_subdomain_enum.py -d example.com
python run_sublist3r.py -d example.com


Results saved as sublist3r_output.txt.

💉 SQL Injection Test
python run_sql_injection.py -u "http://example.com/vuln.php?id=1"

🤖 AI-Powered Analysis
python prompt_handler.py


Takes results (Nmap, Harvester, etc.) → sends to Gemini API → returns analysis.

📄 Generate PDF Report
python report_generator.py


Creates security_report_<timestamp>.pdf.

🔥 Full Workflow
python app.py


Runs scans, AI analysis, and generates a PDF security report in one go.

📊 Example Workflow

Run Nmap + theHarvester + Subdomain Scan

Send results to Gemini AI (prompt_handler.py)

Auto-generate PDF Report (report_generator.py)

📌 Example report: security_report_20250901_115944.pdf

🛠️ Tech Stack

Python 3.9+

Google Gemini API (AI-powered analysis)

Nmap (network scanning)

theHarvester (OSINT email/host collection)

Sublist3r (subdomain enumeration)

ReportLab (PDF generation)

⚠️ Disclaimer

This toolkit is for educational and ethical purposes only.
Do not use it against systems you don’t own or have explicit permission to test.
The author is not responsible for misuse of this software.

📜 License

MIT License © 2025 Gowtham MG
