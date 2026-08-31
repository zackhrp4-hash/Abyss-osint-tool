import json
import re
import socket
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

APP_NAME = "Abyss OSINT Tools"
RESULT_LOG = []

THEMES = {
    "dark": {
        "title": "\033[96m",
        "accent": "\033[92m",
        "info": "\033[94m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "reset": "\033[0m",
    },
    "blue": {
        "title": "\033[36m",
        "accent": "\033[94m",
        "info": "\033[34m",
        "warning": "\033[96m",
        "error": "\033[31m",
        "reset": "\033[0m",
    },
    "neon": {
        "title": "\033[95m",
        "accent": "\033[92m",
        "info": "\033[96m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "reset": "\033[0m",
    },
    "light": {
        "title": "\033[34m",
        "accent": "\033[32m",
        "info": "\033[90m",
        "warning": "\033[33m",
        "error": "\033[31m",
        "reset": "\033[0m",
    },
    "green": {
        "title": "\033[32m",
        "accent": "\033[92m",
        "info": "\033[36m",
        "warning": "\033[33m",
        "error": "\033[31m",
        "reset": "\033[0m",
    },
    "purple": {
        "title": "\033[35m",
        "accent": "\033[93m",
        "info": "\033[94m",
        "warning": "\033[95m",
        "error": "\033[91m",
        "reset": "\033[0m",
    },
    "sunset": {
        "title": "\033[38;5;214m",
        "accent": "\033[38;5;202m",
        "info": "\033[38;5;208m",
        "warning": "\033[38;5;220m",
        "error": "\033[38;5;196m",
        "reset": "\033[0m",
    },
    "crimson": {
        "title": "\033[38;5;161m",
        "accent": "\033[38;5;198m",
        "info": "\033[38;5;201m",
        "warning": "\033[38;5;214m",
        "error": "\033[38;5;196m",
        "reset": "\033[0m",
    },
    "cyan": {
        "title": "\033[38;5;51m",
        "accent": "\033[38;5;87m",
        "info": "\033[38;5;45m",
        "warning": "\033[38;5;111m",
        "error": "\033[38;5;203m",
        "reset": "\033[0m",
    },
    "gold": {
        "title": "\033[38;5;220m",
        "accent": "\033[38;5;178m",
        "info": "\033[38;5;214m",
        "warning": "\033[38;5;226m",
        "error": "\033[38;5;196m",
        "reset": "\033[0m",
    },
    "matrix": {
        "title": "\033[38;5;46m",
        "accent": "\033[38;5;82m",
        "info": "\033[38;5;118m",
        "warning": "\033[38;5;154m",
        "error": "\033[38;5;160m",
        "reset": "\033[0m",
    },
    "mono": {
        "title": "\033[37m",
        "accent": "\033[90m",
        "info": "\033[97m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "reset": "\033[0m",
    },
    "ember": {
        "title": "\033[38;5;202m",
        "accent": "\033[38;5;208m",
        "info": "\033[38;5;214m",
        "warning": "\033[38;5;172m",
        "error": "\033[38;5;124m",
        "reset": "\033[0m",
    },
    "aqua": {
        "title": "\033[38;5;30m",
        "accent": "\033[38;5;50m",
        "info": "\033[38;5;45m",
        "warning": "\033[38;5;86m",
        "error": "\033[38;5;196m",
        "reset": "\033[0m",
    },
    "rose": {
        "title": "\033[38;5;211m",
        "accent": "\033[38;5;219m",
        "info": "\033[38;5;225m",
        "warning": "\033[38;5;216m",
        "error": "\033[38;5;197m",
        "reset": "\033[0m",
    },
    "violet": {
        "title": "\033[38;5;93m",
        "accent": "\033[38;5;135m",
        "info": "\033[38;5;141m",
        "warning": "\033[38;5;177m",
        "error": "\033[38;5;161m",
        "reset": "\033[0m",
    },
    "amber": {
        "title": "\033[38;5;178m",
        "accent": "\033[38;5;214m",
        "info": "\033[38;5;208m",
        "warning": "\033[38;5;220m",
        "error": "\033[38;5;196m",
        "reset": "\033[0m",
    },
    "orchid": {
        "title": "\033[38;5;183m",
        "accent": "\033[38;5;213m",
        "info": "\033[38;5;219m",
        "warning": "\033[38;5;225m",
        "error": "\033[38;5;198m",
        "reset": "\033[0m",
    },
}

CURRENT_THEME = "dark"

def color(text, key):
    return f"{THEMES[CURRENT_THEME][key]}{text}{THEMES[CURRENT_THEME]['reset']}"

def print_header(title):
    print()
    print(color("=" * 60, "title"))
    print(color(title.center(60), "title"))
    print(color("=" * 60, "title"))

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc)}

def log_result(label, output):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    RESULT_LOG.append(f"[{stamp}] {label}\n{output}\n")
    return output

def save_results():
    path = Path(__file__).with_name("osint_results.txt")
    path.write_text("\n".join(RESULT_LOG), encoding="utf-8")
    print(color(f"\nSaved results to: {path}", "accent"))

def view_saved_results():
    path = Path(__file__).with_name("osint_results.txt")
    if not path.exists():
        print(color("\nNo saved results yet.", "warning"))
        return
    print_header("Saved Results")
    print(color(path.read_text(encoding="utf-8"), "info"))

def get_public_ip():
    data = fetch_json("https://api.ipify.org?format=json")
    if "error" in data:
        return log_result("Public IP", f"Error: {data['error']}")
    ip = data.get("ip", "Unknown")
    return log_result("Public IP", f"Public IP: {ip}")

def get_ip_details(ip):
    data = fetch_json(f"https://ipapi.co/{ip}/json/")
    if "error" in data:
        return log_result("IP Details", f"Error: {data['error']}")
    result = (
        f"IP: {ip}\n"
        f"City: {data.get('city', 'Unknown')}\n"
        f"Region: {data.get('region', 'Unknown')}\n"
        f"Country: {data.get('country_name', 'Unknown')}\n"
        f"Organization: {data.get('org', 'Unknown')}\n"
        f"ASN: {data.get('asn', 'Unknown')}\n"
        f"Timezone: {data.get('timezone', 'Unknown')}"
    )
    return log_result("IP Details", result)

def resolve_domain(domain):
    try:
        infos = socket.getaddrinfo(domain, None)
        ips = []
        for info in infos:
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
        result = "No IPs found." if not ips else "Resolved IPs:\n" + "\n".join(f"- {ip}" for ip in ips)
        return log_result(f"Domain Resolution: {domain}", result)
    except Exception as exc:
        return log_result(f"Domain Resolution: {domain}", f"Error: {exc}")

def reverse_dns(ip):
    try:
        host, alias, _ = socket.gethostbyaddr(ip)
        result = f"Reverse DNS for {ip}: {host}"
        if alias:
            result += f"\nAliases: {', '.join(alias)}"
        return log_result(f"Reverse DNS: {ip}", result)
    except Exception as exc:
        return log_result(f"Reverse DNS: {ip}", f"Error: {exc}")

def whois_lookup(target):
    try:
        if sys.platform.startswith("win"):
            proc = subprocess.run(["whois", target], capture_output=True, text=True, timeout=20)
        else:
            proc = subprocess.run(["bash", "-lc", f"whois {target} || true"], capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No WHOIS data returned."
        return log_result(f"WHOIS: {target}", result)
    except Exception as exc:
        return log_result(f"WHOIS: {target}", f"Error: {exc}")

def check_dns(domain):
    lines = [f"DNS records for {domain}"]
    for qtype in ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "SRV"]:
        try:
            if sys.platform.startswith("win"):
                cmd = ["nslookup", "-type=" + qtype, domain]
            else:
                cmd = ["bash", "-lc", f"nslookup -type={qtype} {domain} || true"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            output = (proc.stdout + proc.stderr).strip()
            lines.append(f"\n[{qtype}]\n{output if output else 'No records found'}")
        except Exception as exc:
            lines.append(f"\n[{qtype}]\nError: {exc}")
    result = "\n".join(lines)
    return log_result(f"DNS Check: {domain}", result)

def get_dns_records(domain, qtype):
    try:
        infos = socket.getaddrinfo(domain, None, type=0)
        records = []
        if qtype.upper() == "A":
            for info in infos:
                ip = info[4][0]
                if ":" not in ip and ip not in records:
                    records.append(ip)
            out = ", ".join(records) if records else "No A records found."
        elif qtype.upper() == "AAAA":
            for info in infos:
                ip = info[4][0]
                if ":" in ip and ip not in records:
                    records.append(ip)
            out = ", ".join(records) if records else "No AAAA records found."
        else:
            out = "This helper returns A/AAAA records only."
        return log_result(f"{qtype} Records: {domain}", out)
    except Exception as exc:
        return log_result(f"{qtype} Records: {domain}", f"Error: {exc}")

def dns_mx_records(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=MX", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=MX {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No MX records found."
        return log_result(f"MX Records: {domain}", result)
    except Exception as exc:
        return log_result(f"MX Records: {domain}", f"Error: {exc}")

def dns_ns_records(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=NS", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=NS {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No NS records found."
        return log_result(f"NS Records: {domain}", result)
    except Exception as exc:
        return log_result(f"NS Records: {domain}", f"Error: {exc}")

def dns_txt_records(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=TXT", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=TXT {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No TXT records found."
        return log_result(f"TXT Records: {domain}", result)
    except Exception as exc:
        return log_result(f"TXT Records: {domain}", f"Error: {exc}")

def dns_cname_records(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=CNAME", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=CNAME {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No CNAME records found."
        return log_result(f"CNAME Records: {domain}", result)
    except Exception as exc:
        return log_result(f"CNAME Records: {domain}", f"Error: {exc}")

def dns_soa_records(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=SOA", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=SOA {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No SOA records found."
        return log_result(f"SOA Records: {domain}", result)
    except Exception as exc:
        return log_result(f"SOA Records: {domain}", f"Error: {exc}")

def dns_srv_records(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=SRV", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=SRV {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No SRV records found."
        return log_result(f"SRV Records: {domain}", result)
    except Exception as exc:
        return log_result(f"SRV Records: {domain}", f"Error: {exc}")

def dns_any_records(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=ANY", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=ANY {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No ANY records found."
        return log_result(f"ANY Records: {domain}", result)
    except Exception as exc:
        return log_result(f"ANY Records: {domain}", f"Error: {exc}")

def http_status(url):
    try:
        url = url if "://" in url else "https://" + url
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            result = f"URL: {url}\nStatus: {response.status}\nFinal URL: {response.geturl()}"
            return log_result(f"HTTP Status: {url}", result)
    except Exception as exc:
        try:
            url2 = url if "://" in url else "http://" + url
            req = urllib.request.Request(url2, method="HEAD", headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
            with urllib.request.urlopen(req, timeout=12) as response:
                result = f"URL: {url2}\nStatus: {response.status}\nFinal URL: {response.geturl()}"
                return log_result(f"HTTP Status: {url2}", result)
        except Exception:
            return log_result(f"HTTP Status: {url}", f"Error: {exc}")

def http_headers(url):
    try:
        url = url if "://" in url else "https://" + url
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            headers = response.headers
            result = "\n".join(f"{k}: {v}" for k, v in headers.items())
            return log_result(f"HTTP Headers: {url}", result)
    except Exception as exc:
        return log_result(f"HTTP Headers: {url}", f"Error: {exc}")

def security_headers(url):
    try:
        url = url if "://" in url else "https://" + url
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            headers = response.headers
            targets = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"]
            result = "\n".join(f"{k}: {headers.get(k, 'Missing')}" for k in targets)
            return log_result(f"Security Headers: {url}", result)
    except Exception as exc:
        return log_result(f"Security Headers: {url}", f"Error: {exc}")

def ssl_certificate_info(host):
    try:
        host = host.split("://")[-1].split("/")[0]
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=12) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                subject = cert.get("subject", [])
                issuer = cert.get("issuer", [])
                valid_from = cert.get("notBefore", "Unknown")
                valid_to = cert.get("notAfter", "Unknown")
                result = (
                    f"Host: {host}\n"
                    f"Subject: {subject}\n"
                    f"Issuer: {issuer}\n"
                    f"Valid From: {valid_from}\n"
                    f"Valid To: {valid_to}"
                )
                return log_result(f"SSL Cert: {host}", result)
    except Exception as exc:
        return log_result(f"SSL Cert: {host}", f"Error: {exc}")

def ssl_certificate_issuer(host):
    try:
        host = host.split("://")[-1].split("/")[0]
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=12) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                issuer = cert.get("issuer", [])
                return log_result(f"SSL Issuer: {host}", str(issuer))
    except Exception as exc:
        return log_result(f"SSL Issuer: {host}", f"Error: {exc}")

def tls_versions(host):
    try:
        host = host.split("://")[-1].split("/")[0]
        results = []
        for proto in ["TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"]:
            try:
                ctx = ssl.create_default_context()
                ctx.minimum_version = ssl.TLSVersion.TLSv1
                ctx.maximum_version = ssl.TLSVersion.TLSv1_3
                with socket.create_connection((host, 443), timeout=10) as sock:
                    with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                        results.append(f"{proto}: Supported")
            except Exception:
                results.append(f"{proto}: Unsupported")
        return log_result(f"TLS Versions: {host}", "\n".join(results))
    except Exception as exc:
        return log_result(f"TLS Versions: {host}", f"Error: {exc}")

def port_scan(host, ports="21,22,25,53,80,110,143,443,465,587,993,995,3306,8080,8443,8888"):
    try:
        host = host.split("://")[-1].split("/")[0]
        results = []
        for port in [p.strip() for p in ports.split(",") if p.strip()]:
            try:
                with socket.create_connection((host, int(port)), timeout=1):
                    results.append(f"Port {port}: OPEN")
            except Exception:
                results.append(f"Port {port}: CLOSED")
        result = "\n".join(results) if results else "No ports scanned."
        return log_result(f"Port Scan: {host}", result)
    except Exception as exc:
        return log_result(f"Port Scan: {host}", f"Error: {exc}")

def port_banner(host, port="80"):
    try:
        host = host.split("://")[-1].split("/")[0]
        with socket.create_connection((host, int(port)), timeout=5) as sock:
            sock.settimeout(5)
            sock.sendall(b"HEAD / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
            banner = sock.recv(4096).decode("utf-8", errors="ignore")
            return log_result(f"Banner: {host}:{port}", banner[:2000])
    except Exception as exc:
        return log_result(f"Banner: {host}:{port}", f"Error: {exc}")

def ping_host(host):
    try:
        if sys.platform.startswith("win"):
            cmd = ["ping", "-n", "1", host]
        else:
            cmd = ["ping", "-c", "1", host]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No response."
        return log_result(f"Ping: {host}", result)
    except Exception as exc:
        return log_result(f"Ping: {host}", f"Error: {exc}")

def traceroute(host):
    try:
        if sys.platform.startswith("win"):
            cmd = ["tracert", host]
        else:
            cmd = ["traceroute", host]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No trace route result."
        return log_result(f"Traceroute: {host}", result)
    except Exception as exc:
        return log_result(f"Traceroute: {host}", f"Error: {exc}")

def reverse_ip_lookup(ip):
    try:
        url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
        req = urllib.request.Request(url, headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            body = response.read().decode("utf-8", errors="ignore")
            return log_result(f"Reverse IP: {ip}", body[:4000] if body else "No results.")
    except Exception as exc:
        return log_result(f"Reverse IP: {ip}", f"Error: {exc}")

def check_common_subdomains(domain):
    try:
        common = ["www", "mail", "admin", "login", "vpn", "api", "dev", "ftp", "test", "blog", "shop", "support", "portal", "app", "cdn"]
        results = []
        for sub in common:
            host = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(host)
                results.append(f"{host} -> {ip}")
            except Exception:
                pass
        result = "\n".join(results) if results else "No common subdomains resolved."
        return log_result(f"Common Subdomains: {domain}", result)
    except Exception as exc:
        return log_result(f"Common Subdomains: {domain}", f"Error: {exc}")

def subdomain_bruteforce(domain):
    try:
        common = ["www", "mail", "ftp", "login", "admin", "panel", "api", "dev", "test", "beta", "cdn", "assets", "app", "blog", "shop", "support", "vpn"]
        results = []
        for sub in common:
            host = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(host)
                results.append(f"{host} -> {ip}")
            except Exception:
                pass
        result = "\n".join(results) if results else "No subdomains found."
        return log_result(f"Subdomain Brute Force: {domain}", result)
    except Exception as exc:
        return log_result(f"Subdomain Brute Force: {domain}", f"Error: {exc}")

def url_to_ip(url):
    try:
        host = urllib.parse.urlparse(url if "://" in url else "https://" + url).hostname
        ip = socket.gethostbyname(host)
        return log_result(f"URL to IP: {url}", f"{host} -> {ip}")
    except Exception as exc:
        return log_result(f"URL to IP: {url}", f"Error: {exc}")

def email_extractor(text):
    try:
        pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        found = sorted(set(re.findall(pattern, text)))
        result = "\n".join(found) if found else "No emails found."
        return log_result("Email Extract", result)
    except Exception as exc:
        return log_result("Email Extract", f"Error: {exc}")

def extract_links(url):
    try:
        url = url if "://" in url else "https://" + url
        req = urllib.request.Request(url, headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            page = response.read().decode("utf-8", errors="ignore")
        links = sorted(set(re.findall(r'''https?://[^\s"'<>]+''', page)))
        result = "\n".join(links) if links else "No links found."
        return log_result(f"Page Links: {url}", result)
    except Exception as exc:
        return log_result(f"Page Links: {url}", f"Error: {exc}")

def extract_js_links(url):
    try:
        url = url if "://" in url else "https://" + url
        req = urllib.request.Request(url, headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            page = response.read().decode("utf-8", errors="ignore")
        links = sorted(set(re.findall(r'''(?:src|href)=["']([^"']+\.js(?:\?[^"']*)?)["']''', page, flags=re.I)))
        result = "\n".join(links) if links else "No JS files found."
        return log_result(f"JS Links: {url}", result)
    except Exception as exc:
        return log_result(f"JS Links: {url}", f"Error: {exc}")

def read_robots(url):
    try:
        url = url if "://" in url else "https://" + url
        robots_url = urllib.parse.urljoin(url.rstrip("/") + "/", "/robots.txt")
        req = urllib.request.Request(robots_url, headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            content = response.read().decode("utf-8", errors="ignore")
            return log_result(f"Robots: {robots_url}", content[:4000])
    except Exception as exc:
        return log_result(f"Robots: {url}", f"Error: {exc}")

def read_sitemap(url):
    try:
        url = url if "://" in url else "https://" + url
        sitemap_url = urllib.parse.urljoin(url.rstrip("/") + "/", "/sitemap.xml")
        req = urllib.request.Request(sitemap_url, headers={"User-Agent": "Abyss-OSINT-Tools/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            content = response.read().decode("utf-8", errors="ignore")
            return log_result(f"Sitemap: {sitemap_url}", content[:4000])
    except Exception as exc:
        return log_result(f"Sitemap: {url}", f"Error: {exc}")

def check_spf(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=TXT", domain]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=TXT {domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        matches = [line for line in output.splitlines() if "spf" in line.lower()]
        result = "\n".join(matches) if matches else "No SPF record found."
        return log_result(f"SPF: {domain}", result)
    except Exception as exc:
        return log_result(f"SPF: {domain}", f"Error: {exc}")

def check_dkim(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=TXT", f"selector1._domainkey.{domain}"]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=TXT selector1._domainkey.{domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No DKIM record found."
        return log_result(f"DKIM: {domain}", result)
    except Exception as exc:
        return log_result(f"DKIM: {domain}", f"Error: {exc}")

def check_dmarc(domain):
    try:
        if sys.platform.startswith("win"):
            cmd = ["nslookup", "-type=TXT", f"_dmarc.{domain}"]
        else:
            cmd = ["bash", "-lc", f"nslookup -type=TXT _dmarc.{domain} || true"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = (proc.stdout + proc.stderr).strip()
        result = output if output else "No DMARC record found."
        return log_result(f"DMARC: {domain}", result)
    except Exception as exc:
        return log_result(f"DMARC: {domain}", f"Error: {exc}")

def asn_lookup(ip):
    try:
        data = fetch_json(f"https://ipapi.co/{ip}/json/")
        if "error" in data:
            return log_result(f"ASN: {ip}", f"Error: {data['error']}")
        result = f"ASN: {data.get('asn', 'Unknown')}\nOrg: {data.get('org', 'Unknown')}\nCountry: {data.get('country_name', 'Unknown')}"
        return log_result(f"ASN: {ip}", result)
    except Exception as exc:
        return log_result(f"ASN: {ip}", f"Error: {exc}")

def service_banner(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=5) as sock:
            sock.settimeout(5)
            try:
                banner = sock.recv(4096).decode("utf-8", errors="ignore")
            except Exception:
                banner = ""
            return log_result(f"Service Banner: {host}:{port}", banner[:2000] if banner else "No banner returned.")
    except Exception as exc:
        return log_result(f"Service Banner: {host}:{port}", f"Error: {exc}")

def open_terminal():
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["powershell.exe"], shell=True)
        else:
            subprocess.Popen(["bash"], shell=True)
        print(color("\nTerminal opened.", "accent"))
    except Exception as exc:
        print(color(f"\nFailed to open terminal: {exc}", "error"))

def show_theme_menu():
    print_header("Theme Settings")
    print(color("1. Dark", "info"))
    print(color("2. Blue", "info"))
    print(color("3. Neon", "info"))
    print(color("4. Light", "info"))
    print(color("5. Back", "warning"))

def change_theme():
    while True:
        show_theme_menu()
        choice = input(color("\nSelect a theme (1-5): ", "accent")).strip()
        global CURRENT_THEME
        if choice == "1":
            CURRENT_THEME = "dark"
            print(color("\nTheme changed to Dark.", "accent"))
            break
        elif choice == "2":
            CURRENT_THEME = "blue"
            print(color("\nTheme changed to Blue.", "accent"))
            break
        elif choice == "3":
            CURRENT_THEME = "neon"
            print(color("\nTheme changed to Neon.", "accent"))
            break
        elif choice == "4":
            CURRENT_THEME = "light"
            print(color("\nTheme changed to Light.", "accent"))
            break
        elif choice == "5":
            break
        else:
            print(color("\nInvalid choice. Try again.", "error"))

def show_menu():
    print_header(APP_NAME)
    print(color("1. Show public IP", "info"))
    print(color("2. IP details lookup", "info"))
    print(color("3. Resolve domain", "info"))
    print(color("4. DNS records", "info"))
    print(color("5. Reverse DNS", "info"))
    print(color("6. WHOIS lookup", "info"))
    print(color("7. DNS A records", "info"))
    print(color("8. DNS AAAA records", "info"))
    print(color("9. MX records", "info"))
    print(color("10. NS records", "info"))
    print(color("11. TXT records", "info"))
    print(color("12. CNAME records", "info"))
    print(color("13. SOA records", "info"))
    print(color("14. SRV records", "info"))
    print(color("15. ANY records", "info"))
    print(color("16. HTTP status", "info"))
    print(color("17. HTTP headers", "info"))
    print(color("18. Security headers", "info"))
    print(color("19. SSL certificate", "info"))
    print(color("20. SSL issuer", "info"))
    print(color("21. TLS versions", "info"))
    print(color("22. Port scan", "info"))
    print(color("23. Banner grab", "info"))
    print(color("24. Ping host", "info"))
    print(color("25. Traceroute", "info"))
    print(color("26. Reverse IP lookup", "info"))
    print(color("27. Common subdomains", "info"))
    print(color("28. Subdomain brute force", "info"))
    print(color("29. URL to IP", "info"))
    print(color("30. Extract links", "info"))
    print(color("31. Extract JS links", "info"))
    print(color("32. Robots.txt", "info"))
    print(color("33. Sitemap.xml", "info"))
    print(color("34. SPF record", "info"))
    print(color("35. DKIM record", "info"))
    print(color("36. DMARC record", "info"))
    print(color("37. ASN lookup", "info"))
    print(color("38. Service banner", "info"))
    print(color("39. Email extractor", "info"))
    print(color("40. Save results", "warning"))
    print(color("41. View saved results", "warning"))
    print(color("42. Open terminal", "warning"))
    print(color("43. Settings", "warning"))
    print(color("44. Exit", "warning"))

def main():
    while True:
        show_menu()
        choice = input(color("\nSelect an option (1-44): ", "accent")).strip()

        if choice == "1":
            print_header("Public IP")
            print(get_public_ip())
        elif choice == "2":
            ip = input(color("Enter IP: ", "accent")).strip()
            print_header(f"IP Details: {ip}")
            print(get_ip_details(ip))
        elif choice == "3":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"Domain Resolution: {domain}")
            print(resolve_domain(domain))
        elif choice == "4":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"DNS Check: {domain}")
            print(check_dns(domain))
        elif choice == "5":
            ip = input(color("Enter IP: ", "accent")).strip()
            print_header(f"Reverse DNS: {ip}")
            print(reverse_dns(ip))
        elif choice == "6":
            target = input(color("Enter target: ", "accent")).strip()
            print_header(f"WHOIS: {target}")
            print(whois_lookup(target))
        elif choice == "7":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"A Records: {domain}")
            print(get_dns_records(domain, "A"))
        elif choice == "8":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"AAAA Records: {domain}")
            print(get_dns_records(domain, "AAAA"))
        elif choice == "9":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"MX Records: {domain}")
            print(dns_mx_records(domain))
        elif choice == "10":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"NS Records: {domain}")
            print(dns_ns_records(domain))
        elif choice == "11":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"TXT Records: {domain}")
            print(dns_txt_records(domain))
        elif choice == "12":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"CNAME Records: {domain}")
            print(dns_cname_records(domain))
        elif choice == "13":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"SOA Records: {domain}")
            print(dns_soa_records(domain))
        elif choice == "14":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"SRV Records: {domain}")
            print(dns_srv_records(domain))
        elif choice == "15":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"ANY Records: {domain}")
            print(dns_any_records(domain))
        elif choice == "16":
            url = input(color("Enter URL or host: ", "accent")).strip()
            print_header(f"HTTP Status: {url}")
            print(http_status(url))
        elif choice == "17":
            url = input(color("Enter URL or host: ", "accent")).strip()
            print_header(f"HTTP Headers: {url}")
            print(http_headers(url))
        elif choice == "18":
            url = input(color("Enter URL or host: ", "accent")).strip()
            print_header(f"Security Headers: {url}")
            print(security_headers(url))
        elif choice == "19":
            host = input(color("Enter host: ", "accent")).strip()
            print_header(f"SSL Certificate: {host}")
            print(ssl_certificate_info(host))
        elif choice == "20":
            host = input(color("Enter host: ", "accent")).strip()
            print_header(f"SSL Issuer: {host}")
            print(ssl_certificate_issuer(host))
        elif choice == "21":
            host = input(color("Enter host: ", "accent")).strip()
            print_header(f"TLS Versions: {host}")
            print(tls_versions(host))
        elif choice == "22":
            host = input(color("Enter host: ", "accent")).strip()
            print_header(f"Port Scan: {host}")
            print(port_scan(host))
        elif choice == "23":
            host = input(color("Enter host: ", "accent")).strip()
            port = input(color("Enter port: ", "accent")).strip()
            print_header(f"Banner Grab: {host}:{port}")
            print(port_banner(host, port))
        elif choice == "24":
            host = input(color("Enter host: ", "accent")).strip()
            print_header(f"Ping: {host}")
            print(ping_host(host))
        elif choice == "25":
            host = input(color("Enter host: ", "accent")).strip()
            print_header(f"Traceroute: {host}")
            print(traceroute(host))
        elif choice == "26":
            ip = input(color("Enter IP: ", "accent")).strip()
            print_header(f"Reverse IP: {ip}")
            print(reverse_ip_lookup(ip))
        elif choice == "27":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"Common Subdomains: {domain}")
            print(check_common_subdomains(domain))
        elif choice == "28":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"Subdomain Brute Force: {domain}")
            print(subdomain_bruteforce(domain))
        elif choice == "29":
            url = input(color("Enter URL: ", "accent")).strip()
            print_header(f"URL to IP: {url}")
            print(url_to_ip(url))
        elif choice == "30":
            url = input(color("Enter URL: ", "accent")).strip()
            print_header(f"Page Links: {url}")
            print(extract_links(url))
        elif choice == "31":
            url = input(color("Enter URL: ", "accent")).strip()
            print_header(f"JS Links: {url}")
            print(extract_js_links(url))
        elif choice == "32":
            url = input(color("Enter URL or domain: ", "accent")).strip()
            print_header(f"Robots.txt: {url}")
            print(read_robots(url))
        elif choice == "33":
            url = input(color("Enter URL or domain: ", "accent")).strip()
            print_header(f"Sitemap.xml: {url}")
            print(read_sitemap(url))
        elif choice == "34":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"SPF: {domain}")
            print(check_spf(domain))
        elif choice == "35":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"DKIM: {domain}")
            print(check_dkim(domain))
        elif choice == "36":
            domain = input(color("Enter domain: ", "accent")).strip()
            print_header(f"DMARC: {domain}")
            print(check_dmarc(domain))
        elif choice == "37":
            ip = input(color("Enter IP: ", "accent")).strip()
            print_header(f"ASN: {ip}")
            print(asn_lookup(ip))
        elif choice == "38":
            host = input(color("Enter host: ", "accent")).strip()
            port = input(color("Enter port: ", "accent")).strip()
            print_header(f"Service Banner: {host}:{port}")
            print(service_banner(host, port))
        elif choice == "39":
            text = input(color("Paste text to scan for emails: ", "accent"))
            print_header("Email Extract")
            print(email_extractor(text))
        elif choice == "40":
            save_results()
        elif choice == "41":
            view_saved_results()
        elif choice == "42":
            open_terminal()
        elif choice == "43":
            change_theme()
        elif choice == "44":
            print(color("\nGoodbye.", "accent"))
            break
        else:
            print(color("\nInvalid option. Choose a number from 1 to 44.", "error"))

if __name__ == "__main__":
    main()
