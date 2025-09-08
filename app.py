# app.py
import streamlit as st
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from run_nmap import run_nmap_scan
from run_harvester import run_harvester_scan
from run_sublist3r import run_sublist3r
from run_sql_injection import run_sql_injection
from run_subdomain_enum import run_custom_subdomain_enum
from prompt_handler import analyze_results_with_ai
from report_generator import generate_report

st.set_page_config(page_title="GenAI Ethical Hacking Toolkit", layout="wide")
st.title("🛡️ GenAI-Powered Ethical Hacking Toolkit")
st.write("Automated Recon + AI Analysis + Single PDF Report Generation (Black Text)")

# ------------------------
# User Input
# ------------------------
target = st.text_input("Enter Target (Domain/IP):", "").strip()
scan_options = st.multiselect(
    "Select Scans to Run:",
    ["Nmap", "theHarvester", "Sublist3r", "SQL Injection", "Subdomain Enum", "All"],
)

# ------------------------
# Scan Tool Runner
# ------------------------
def run_tool(tool_name: str, target: str):
    """Safely run a scan tool and return its output."""
    try:
        if tool_name == "Nmap":
            return run_nmap_scan(target)
        elif tool_name == "theHarvester":
            return run_harvester_scan(target)
        elif tool_name == "Sublist3r":
            return run_sublist3r(target)
        elif tool_name == "SQL Injection":
            return run_sql_injection(target)
        elif tool_name == "Subdomain Enum":
            return run_custom_subdomain_enum(target)
        else:
            return {"error": "Unknown tool"}
    except Exception as e:
        return {"error": f"{tool_name} scan failed: {str(e)}"}

# ------------------------
# Main Scan & AI Analysis
# ------------------------
if st.button("🚀 Run Selected Scans"):
    if not target:
        st.error("⚠️ Please enter a target before running the scan.")
    else:
        results = {}
        ai_reports = {}

        # Determine tools to run
        tools_to_run = (
            ["Nmap", "theHarvester", "Sublist3r", "SQL Injection", "Subdomain Enum"]
            if "All" in scan_options
            else scan_options
        )

        # Run scans in parallel
        with ThreadPoolExecutor() as executor:
            future_to_tool = {executor.submit(run_tool, tool, target): tool for tool in tools_to_run}
            for future in as_completed(future_to_tool):
                tool = future_to_tool[future]
                st.info(f"🔍 Running {tool}...")
                output = future.result()
                key = tool.lower().replace(" ", "_")
                results[key] = output

                # Display raw results
                st.subheader(f"🔹 {tool} Results")
                if isinstance(output, dict):
                    st.json(output)
                else:
                    st.text(output)

                # Run AI analysis for this tool
                st.info(f"🤖 Generating AI analysis for {tool}...")
                ai_output = analyze_results_with_ai(output, tool=key)
                ai_reports[key] = ai_output or "AI analysis unavailable."
                st.subheader(f"🤖 AI Analysis ({tool})")
                st.write(ai_output)

        # Overall AI summary
        st.info("📊 Generating overall AI analysis...")
        ai_reports["overall"] = analyze_results_with_ai(results, tool="overall") or "AI analysis unavailable."
        st.subheader("📊 Overall AI Security Summary")
        st.write(ai_reports["overall"])

        # ------------------------
        # Generate Single Polished PDF
        # ------------------------
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"security_report_{timestamp}.pdf"

        # Call the generate_report function (ensure AI text is black in report_generator.py)
        generate_report(results, ai_reports, target=target, filename=report_filename)

        # Provide download button
        with open(report_filename, "rb") as f:
            st.download_button(
                "📥 Download Final Report (All Tools + AI Analysis in Black Text)",
                data=f,
                file_name=report_filename,
                mime="application/pdf"
            )

        st.success("✅ Scans completed, AI analyses generated, and PDF report created!")
