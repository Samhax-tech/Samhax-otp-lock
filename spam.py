#!/data/data/com.termux/files/usr/bin/python3
# rD4DDY SAMHAX BAN TOOL v3.0 - ULTIMATE EDITION
# Owner: Samhax | Architect: MR SAMHAX

import os
import sys
import time
import requests
import json
import threading
import smtplib
import ssl
from email.message import EmailMessage
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama and dotenv
init(autoreset=True)
load_dotenv()

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

# Global constants
API_VERSION = "v21.0"
DEFAULT_ACCESS_TOKEN = os.getenv('WA_ACCESS_TOKEN', '')
DEFAULT_PHONE_NUMBER_ID = os.getenv('WA_PHONE_NUMBER_ID', '')

# Gmail Config
SENDER_EMAIL = os.getenv('GMAIL_ADDRESS')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
SUPPORT_EMAILS = [
    "support@whatsapp.com",
    "abuse@support.whatsapp.com",
    "privacy@support.whatsapp.com",
    "terms@support.whatsapp.com",
    "accessibility@support.whatsapp.com"
]

# Ban Files
PERM_FILE = "perm_ban.txt"
LOG_FILE = "session_logs.json"

def banner():
    """Display tool banner"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""
{RED}███████╗ █████╗ ███╗   ███╗██╗  ██╗ █████╗ ██╗  ██╗
██╔════╝██╔══██╗████╗ ████║██║  ██║██╔══██╗╚██╗██╔╝
███████╗███████║██╔████╔██║███████║███████║ ╚███╔╝ 
╚════██║██╔══██║██║╚██╔╝██║██╔══██║██╔══██║ ██╔██╗ 
███████║██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║██╔╝ ██╗
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
{BLUE}          rD4DDY SAMHAX BAN TOOL v3.0{RESET}
{MAGENTA}       THE ULTIMATE WHATSAPP BAN CONSOLE{RESET}
    """)

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_idx = 0
        self.lock = threading.Lock()
    
    def load_proxies(self, proxy_file: str):
        try:
            if not os.path.exists(proxy_file): return
            with open(proxy_file, 'r') as f:
                for line in f:
                    proxy = line.strip()
                    if proxy and not proxy.startswith('#'):
                        parts = proxy.split(':')
                        if len(parts) == 4:
                            self.proxies.append(f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}")
                        else:
                            self.proxies.append(f"http://{proxy}")
            print(f"{GREEN}[+] Loaded {len(self.proxies)} proxies{RESET}")
        except Exception as e:
            print(f"{RED}[-] Error loading proxies: {e}{RESET}")
    
    def get_next(self) -> Dict:
        if not self.proxies: return {}
        with self.lock:
            proxy = self.proxies[self.current_idx]
            self.current_idx = (self.current_idx + 1) % len(self.proxies)
            return {"http": proxy, "https": proxy}

class BanTool:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.access_token = DEFAULT_ACCESS_TOKEN
        self.phone_number_id = DEFAULT_PHONE_NUMBER_ID
        self.options = {
            "1": ("Check Number Status", self.check_number_status),
            "2": ("Report Number (API Only)", self.report_api_only),
            "3": ("Report Number (Mail Only)", self.report_mail_only),
            "4": ("Dual Strike (API + Mail)", self.dual_strike),
            "5": ("Unban Request (Mail)", self.unban_request),
            "6": ("View Ban Records & Logs", self.view_logs),
            "7": ("Configure API Settings", self.configure_api),
            "0": ("Exit Console", self.exit_tool)
        }
    
    def configure_api(self):
        banner()
        print(f"{BLUE}API Configuration:{RESET}")
        self.access_token = input(f"Enter Access Token [{self.access_token[:10]}...]: ") or self.access_token
        self.phone_number_id = input(f"Enter Phone Number ID [{self.phone_number_id}]: ") or self.phone_number_id
        print(f"{GREEN}[+] Settings updated!{RESET}")
        input("\nPress Enter to continue...")

    def show_menu(self):
        banner()
        print(f"{CYAN}Available Operations:{RESET}")
        for key, (desc, _) in self.options.items():
            print(f"{YELLOW}{key}. {desc}{RESET}")
        print(f"{CYAN}\nSelect command [0-7]: {RESET}", end="")

    def check_number_status(self):
        if not self.access_token or not self.phone_number_id:
            print(f"{RED}[-] API Credentials required!{RESET}")
            input("\nPress Enter to continue...")
            return
            
        target = input(f"{WHITE}Enter target number (with country code): {RESET}").strip()
        if not target: return
            
        url = f"https://graph.facebook.com/{API_VERSION}/{self.phone_number_id}/contacts"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "blocking": "wait", "contacts": [f"+{target}" if not target.startswith('+') else target]}
        
        try:
            print(f"{YELLOW}[*] Querying WhatsApp database for {target}...{RESET}")
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                contact = data["data"][0]
                status = contact.get("status", "unknown")
                print(f"\n{GREEN}Result for {target}:{RESET}")
                print(f"Status: {status.upper()}")
                if status == "valid":
                    print(f"{GREEN}[+] Number is ACTIVE on WhatsApp.{RESET}")
                else:
                    print(f"{RED}[-] Number is NOT on WhatsApp or BANNED.{RESET}")
            else:
                print(f"{RED}[-] API Error: {data.get('error', {}).get('message', 'Unknown')}{RESET}")
        except Exception as e:
            print(f"{RED}[-] Connection Error: {e}{RESET}")
        input("\nPress Enter to continue...")

    def report_api_only(self):
        target = input(f"{WHITE}Enter target number to report: {RESET}").strip()
        if not target: return
        try:
            count = int(input(f"{WHITE}Enter number of reports (e.g., 100): {RESET}") or "10")
            delay = float(input(f"{WHITE}Enter delay (seconds, default 0.1): {RESET}") or "0.1")
        except ValueError: return

        print(f"\n{RED}💣 Deploying API-only strike on {target}...{RESET}")
        success = 0
        for i in range(count):
            res = self._api_block(target)
            if res.get("success"): success += 1
            print(f"{RED}☠️ [{i+1}/{count}] API Packet Sent → {target} ({'OK' if res.get('success') else 'FAIL'})")
            time.sleep(delay)
        
        print(f"\n{GREEN}[+] Operation Complete. Success: {success}/{count}{RESET}")
        self._log_session("API_STRIKE", target, count, success)
        input("\nPress Enter to continue...")

    def report_mail_only(self):
        target = input(f"{WHITE}Enter target number to report: {RESET}").strip()
        if not target: return
        try:
            count = int(input(f"{WHITE}Enter number of reports (e.g., 50): {RESET}") or "10")
            delay = float(input(f"{WHITE}Enter delay (seconds, default 1.0): {RESET}") or "1.0")
        except ValueError: return

        reason = self._get_ban_reason()
        print(f"\n{MAGENTA}📧 Deploying Mail-only strike on {target}...{RESET}")
        success = 0
        for i in range(count):
            res = self._send_mail(target, "Report of WhatsApp Account Violation", reason, i+1, count)
            if res: success += 1
            print(f"{MAGENTA}✉️ [{i+1}/{count}] Mail Sent to Support → {target} ({'OK' if res else 'FAIL'})")
            time.sleep(delay)
        
        print(f"\n{GREEN}[+] Operation Complete. Success: {success}/{count}{RESET}")
        self._log_session("MAIL_STRIKE", target, count, success)
        input("\nPress Enter to continue...")

    def dual_strike(self):
        target = input(f"{WHITE}Enter target number for DUAL STRIKE: {RESET}").strip()
        if not target: return
        try:
            count = int(input(f"{WHITE}Enter number of reports (e.g., 100): {RESET}") or "10")
            delay = float(input(f"{WHITE}Enter delay (seconds, default 0.5): {RESET}") or "0.5")
        except ValueError: return

        reason = self._get_ban_reason()
        print(f"\n{RED}⚡ INITIATING DUAL STRIKE (API + MAIL) ON {target} ⚡{RESET}")
        api_success = 0
        mail_success = 0
        
        for i in range(count):
            # API Vector
            api_res = self._api_block(target)
            if api_res.get("success"): api_success += 1
            
            # Mail Vector
            mail_res = self._send_mail(target, "Urgent: Severe Policy Violation Report", reason, i+1, count)
            if mail_res: mail_success += 1
            
            print(f"{RED}☠️ [{i+1}/{count}] DUAL VECTOR → {target} (API: {'OK' if api_res.get('success') else 'FAIL'} | Mail: {'OK' if mail_res else 'FAIL'})")
            time.sleep(delay)
            
        print(f"\n{GREEN}[+] DUAL STRIKE COMPLETE.{RESET}")
        print(f"API Success: {api_success} | Mail Success: {mail_success}")
        self._log_session("DUAL_STRIKE", target, count, api_success)
        input("\nPress Enter to continue...")

    def unban_request(self):
        target = input(f"{WHITE}Enter number to request UNBAN: {RESET}").strip()
        if not target: return
        
        reason = f"Hello WhatsApp Support, My number {target} has been banned by mistake. I am a law-abiding user and I have not violated any terms of service. Please review my account and unban it as soon as possible. Thank you."
        print(f"\n{CYAN}🕊️ Sending Unban Request for {target}...{RESET}")
        res = self._send_mail(target, "Request to Unban My WhatsApp Account", reason, 1, 1)
        if res:
            print(f"{GREEN}[+] Unban request sent successfully.{RESET}")
        else:
            print(f"{RED}[-] Failed to send unban request.{RESET}")
        input("\nPress Enter to continue...")

    def _api_block(self, target: str) -> Dict:
        if not self.access_token or not self.phone_number_id:
            return {"success": False, "error": "Missing API Config"}
            
        url = f"https://graph.facebook.com/{API_VERSION}/{self.phone_number_id}/block_users"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        # FIXED SCHEMA: Added messaging_product and correct block_users structure
        payload = {
            "messaging_product": "whatsapp",
            "users": [target]
        }
        
        try:
            proxy = self.proxy_manager.get_next()
            response = requests.post(url, headers=headers, json=payload, proxies=proxy if proxy else None, timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("error", {}).get("message", "Unknown")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_mail(self, target, subject, reason, attempt, total) -> bool:
        if not SENDER_EMAIL or not GMAIL_PASSWORD: return False
        try:
            context = ssl.create_default_context()
            msg = EmailMessage()
            msg['Subject'] = f"{subject} (Ref: {attempt}/{total})"
            msg['From'] = SENDER_EMAIL
            msg['To'] = ", ".join(SUPPORT_EMAILS)
            msg.set_content(f"Target: {target}\n\nReason: {reason}\n\nPlease take immediate action.")
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(SENDER_EMAIL, GMAIL_PASSWORD)
                server.send_message(msg)
            return True
        except: return False

    def _get_ban_reason(self) -> str:
        return "This number is violating WhatsApp terms by spreading malware, scamming users, and sharing prohibited content. Multiple users have reported this account for fraudulent activities. Please disable this account immediately to protect the community."

    def _log_session(self, type, target, count, success):
        log_entry = {
            "timestamp": time.ctime(),
            "type": type,
            "target": target,
            "total_requests": count,
            "successful": success
        }
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                try: logs = json.load(f)
                except: pass
        logs.append(log_entry)
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)

    def view_logs(self):
        banner()
        print(f"{CYAN}--- SESSION LOGS ---{RESET}")
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                try:
                    logs = json.load(f)
                    for log in logs[-10:]: # Show last 10
                        print(f"[{log['timestamp']}] {log['type']} | Target: {log['target']} | Success: {log['successful']}/{log['total_requests']}")
                except: print("No valid logs found.")
        else: print("No logs available.")
        input("\nPress Enter to continue...")

    def exit_tool(self):
        print(f"{RED}\n[!] SHUTTING DOWN CONSOLE...{RESET}")
        sys.exit(0)

    def run(self):
        if os.path.exists("proxiex.txt"): self.proxy_manager.load_proxies("proxiex.txt")
        while True:
            try:
                self.show_menu()
                choice = input().strip()
                if choice in self.options:
                    self.options[choice][1]()
                else:
                    print(f"{RED}[-] Invalid Command.{RESET}")
                    time.sleep(1)
            except KeyboardInterrupt: self.exit_tool()
            except Exception as e:
                print(f"{RED}[-] System Error: {e}{RESET}")
                time.sleep(2)

if __name__ == "__main__":
    BanTool().run()
