#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import io
import os
import subprocess
import argparse
import concurrent.futures
from typing import List, Dict, Any

# Make Windows stdout handle UTF-8 to avoid UnicodeEncodeError
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass  # ignore if not a real TTY

# ---------- Optional auto-install of dnspython ----------
DNS_AVAILABLE = False
def _ensure_dnspython() -> bool:
    global DNS_AVAILABLE
    try:
        import dns.resolver  # noqa: F401
        DNS_AVAILABLE = True
        return True
    except Exception:
        # try to auto-install into *this* interpreter
        try:
            print("[i] dnspython not found. Attempting auto-install: python -m pip install dnspython")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "dnspython"])
            import dns.resolver  # noqa: F401
            DNS_AVAILABLE = True
            return True
        except Exception as e:
            print(f"[!] Could not import/install dnspython: {e}")
            DNS_AVAILABLE = False
            return False

_ensure_dnspython()

import requests  # requests is used for HTTP probing


# ------------------ Core functions ------------------

def check_dns(subdomain_fqdn: str) -> Dict[str, Any]:
    """Resolve A records for a subdomain. Returns dict with either 'ip' or 'error'."""
    if not DNS_AVAILABLE:
        return {"subdomain": subdomain_fqdn, "error": "DNS_UNAVAILABLE"}
    try:
        import dns.resolver
        answers = dns.resolver.resolve(subdomain_fqdn, "A", lifetime=3)
        ip_addresses = [str(rdata) for rdata in answers]
        return {"subdomain": subdomain_fqdn, "ip": ip_addresses, "status": "active"}
    except Exception as e:
        # Normalize common dnspython exceptions into short strings
        errname = getattr(e, "__class__", type("X",(object,),{})).__name__
        return {"subdomain": subdomain_fqdn, "error": errname}


def check_http(subdomain_fqdn: str, https_first: bool = False, timeout: float = 5.0):
    """Return first reachable HTTP status (int) or 'unreachable'."""
    schemes = ("https", "http") if https_first else ("http", "https")
    for scheme in schemes:
        url = f"{scheme}://{subdomain_fqdn}"
        try:
            r = requests.get(url, timeout=timeout, allow_redirects=True)
            return int(r.status_code)
        except requests.RequestException:
            continue
    return "unreachable"


def enumerate_subdomains(domain: str,
                         subnames: List[str],
                         threads: int = 10,
                         force_http_on_dns_fail: bool = True,
                         https_first: bool = False) -> List[Dict[str, Any]]:
    """
    For each subname, run DNS (if available). If DNS fails or is unavailable and
    force_http_on_dns_fail is True, try HTTP probing so the run never hard-fails.
    """
    results: List[Dict[str, Any]] = []
    fqdn_list = [f"{s.strip()}.{domain}".strip(".") for s in subnames if s.strip()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        future_map = {ex.submit(check_dns, fqdn): fqdn for fqdn in fqdn_list}

        for fut in concurrent.futures.as_completed(future_map):
            dns_res = fut.result()

            # decide whether to HTTP probe
            do_http = ("error" not in dns_res) or force_http_on_dns_fail
            if do_http:
                http_status = check_http(dns_res["subdomain"], https_first=https_first)
                dns_res["http_status"] = http_status

            # progress output
            if "error" in dns_res:
                print(f"[-] {dns_res['subdomain']} DNS error: {dns_res['error']}"
                      + (f" | HTTP: {dns_res.get('http_status')}" if do_http else ""))
            else:
                print(f"[+] {dns_res['subdomain']} -> {dns_res['ip']} | HTTP: {dns_res.get('http_status')}")

            results.append(dns_res)

    return results


def load_wordlist(path: str) -> List[str]:
    if not path or not os.path.isfile(path):
        return ["www", "mail", "ftp", "test", "dev", "api", "staging", "beta", "portal", "admin"]
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


# ------------------ CLI ------------------

def main():
    p = argparse.ArgumentParser(description="Subdomain enumeration with DNS + HTTP fallback")
    p.add_argument("domain", help="Target domain, e.g. example.com")
    p.add_argument("-w", "--wordlist", help="Path to subdomain wordlist", default=None)
    p.add_argument("-t", "--threads", type=int, default=10, help="Number of worker threads (default 10)")
    p.add_argument("--no-http-fallback", action="store_true",
                   help="Do NOT probe HTTP when DNS fails or is unavailable")
    p.add_argument("--https-first", action="store_true", help="Try HTTPS before HTTP when probing")
    args = p.parse_args()

    subs = load_wordlist(args.wordlist)
    print(f"[i] Enumerating {len(subs)} candidates for {args.domain} "
          f"(DNS available: {DNS_AVAILABLE}, HTTP fallback: {not args.no_http_fallback})")

    results = enumerate_subdomains(
        domain=args.domain,
        subnames=subs,
        threads=args.threads,
        force_http_on_dns_fail=not args.no_http_fallback,
        https_first=args.https_first,
    )

    # Summary
    alive_dns = [r for r in results if "ip" in r]
    alive_http = [r for r in results if r.get("http_status") not in (None, "unreachable")]
    print("\n== Summary ==")
    print(f"DNS-resolved: {len(alive_dns)} / {len(results)}")
    print(f"HTTP reachable: {len(alive_http)} / {len(results)}")

    # Optional: write JSON/CSV here if you want


if __name__ == "__main__":
    main()
