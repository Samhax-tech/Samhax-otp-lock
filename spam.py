#!/data/data/com.termux/files/usr/bin/python3
# rD4DDY SAMHAX BAN TOOL v2.1 - Fixed for WhatsApp Business API
# Owner: Samhax

import os
import sys
import time
import requests
import json
import threading
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Global constants
API_VERSION = "v21.0"
DEFAULT_ACCESS_TOKEN = "" 
DEFAULT_PHONE_NUMBER_ID = ""

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
{BLUE}          rD4DDY SAMHAX BAN TOOL v2.1{RESET}
{YELLOW}       FIXED FOR WHATSAPP BUSINESS API{RESET}
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

class MenuSystem:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.access_token = DEFAULT_ACCESS_TOKEN
        self.phone_number_id = DEFAULT_PHONE_NUMBER_ID
        self.phone_numbers = []
        self.options = {
            "1": ("Check Number Status", self.check_number_status),
            "2": ("Block/Report Single Number", self.report_single_number),
            "3": ("Targeted Multi-Report (1-100x)", self.targeted_multi_report),
            "4": ("Mass Block Numbers (from file)", self.mass_report_numbers),
            "5": ("Load Proxies", self.load_proxies_menu),
            "6": ("Load Target Numbers", self.load_phone_numbers_menu),
            "7": ("Configure API Settings", self.configure_api),
            "0": ("Exit", self.exit_tool)
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
        print(f"{BLUE}Available Options:{RESET}")
        for key, (desc, _) in self.options.items():
            print(f"{YELLOW}{key}. {desc}{RESET}")
        print(f"{BLUE}\nEnter option number: {RESET}", end="")
    
    def load_proxies_menu(self):
        proxy_file = input("Enter proxy file path (default: proxiex.txt): ") or "proxiex.txt"
        self.proxy_manager.load_proxies(proxy_file)
        input("\nPress Enter to continue...")
    
    def load_phone_numbers_menu(self):
        phone_file = input("Enter target numbers file path (default: phones.txt): ") or "phones.txt"
        try:
            if os.path.exists(phone_file):
                with open(phone_file, 'r') as f:
                    self.phone_numbers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                print(f"{GREEN}[+] Loaded {len(self.phone_numbers)} numbers{RESET}")
            else:
                print(f"{RED}[-] File not found{RESET}")
        except Exception as e:
            print(f"{RED}[-] Error: {e}{RESET}")
        input("\nPress Enter to continue...")

    def check_number_status(self):
        if not self.access_token or not self.phone_number_id:
            print(f"{RED}[-] API Token and Phone Number ID required!{RESET}")
            input("\nPress Enter to continue...")
            return
            
        target = input("Enter target phone number (with country code): ")
        if not target: return
            
        url = f"https://graph.facebook.com/{API_VERSION}/{self.phone_number_id}/contacts"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        payload = {"blocking": "wait", "contacts": [f"+{target}" if not target.startswith('+') else target]}
        
        try:
            print(f"{YELLOW}[*] Checking status for {target}...{RESET}")
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                contact = data["data"][0]
                status = contact.get("status", "unknown")
                wa_id = contact.get("wa_id", "N/A")
                print(f"\n{GREEN}Result for {target}:{RESET}")
                print(f"Status: {status.upper()}")
                print(f"WhatsApp ID: {wa_id}")
            else:
                print(f"{RED}[-] Number not found or API error: {data.get('error', {}).get('message', 'Unknown')}{RESET}")
        except Exception as e:
            print(f"{RED}[-] Error: {e}{RESET}")
        input("\nPress Enter to continue...")

    def report_single_number(self):
        if not self.access_token or not self.phone_number_id:
            print(f"{RED}[-] API Token and Phone Number ID required!{RESET}")
            input("\nPress Enter to continue...")
            return
            
        target = input("Enter target phone number to block: ")
        if not target: return
        
        result = self._block_number(target)
        if result.get("success"):
            print(f"{GREEN}[+] Successfully blocked/reported {target}{RESET}")
        else:
            print(f"{RED}[-] Failed: {result.get('error')}{RESET}")
        input("\nPress Enter to continue...")

    def targeted_multi_report(self):
        if not self.access_token or not self.phone_number_id:
            print(f"{RED}[-] API Token and Phone Number ID required!{RESET}")
            input("\nPress Enter to continue...")
            return
            
        target = input("Enter target phone number to report: ")
        if not target: return
        
        try:
            count = int(input("Enter number of reports (1-100, default 10): ") or "10")
            if count > 100: count = 100
            delay = float(input("Enter delay between reports (seconds, default 0.5): ") or "0.5")
        except ValueError:
            print(f"{RED}[-] Invalid input. Using defaults.{RESET}")
            count = 10
            delay = 0.5
            
        print(f"{BLUE}[+] Starting targeted multi-report for {target} ({count} times)...{RESET}")
        
        success_count = 0
        fail_count = 0
        
        for i in range(count):
            result = self._block_number(target)
            if result.get("success"):
                success_count += 1
                print(f"{GREEN}[{i+1}/{count}] Report sent successfully{RESET}")
            else:
                fail_count += 1
                print(f"{RED}[{i+1}/{count}] Failed: {result.get('error')}{RESET}")
            
            if i < count - 1:
                time.sleep(delay)
                
        print(f"\n{BLUE}Operation Summary:{RESET}")
        print(f"Total: {count} | Success: {GREEN}{success_count}{RESET} | Failed: {RED}{fail_count}{RESET}")
        input("\nPress Enter to continue...")

    def _block_number(self, target: str) -> Dict:
        url = f"https://graph.facebook.com/{API_VERSION}/{self.phone_number_id}/block_users"
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        payload = {"users": [target]}
        
        try:
            proxy = self.proxy_manager.get_next()
            response = requests.post(url, headers=headers, json=payload, proxies=proxy if proxy else None, timeout=15)
            if response.status_code == 200:
                return {"success": True, "response": response.json()}
            else:
                return {"success": False, "error": response.json().get("error", {}).get("message", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def mass_report_numbers(self):
        if not self.phone_numbers:
            print(f"{RED}[-] No target numbers loaded!{RESET}")
            input("\nPress Enter to continue...")
            return
            
        print(f"{BLUE}[+] Starting mass block for {len(self.phone_numbers)} numbers...{RESET}")
        with ThreadPoolExecutor(max_workers=5) as executor:
            for target in self.phone_numbers:
                executor.submit(self._block_number, target)
                print(f"{YELLOW}[*] Block request sent for {target}{RESET}")
                time.sleep(0.5)
        
        print(f"{GREEN}[+] Mass operation completed.{RESET}")
        input("\nPress Enter to continue...")

    def exit_tool(self):
        print(f"{GREEN}[+] Exiting...{RESET}")
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
                    print(f"{RED}[-] Invalid option{RESET}")
                    time.sleep(1)
            except KeyboardInterrupt: self.exit_tool()
            except Exception as e:
                print(f"{RED}[-] Error: {e}{RESET}")
                time.sleep(2)

if __name__ == "__main__":
    MenuSystem().run()
