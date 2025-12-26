#!/usr/bin/env python3
# rD4DDY SAMHAX BAN TOOL v2.1
# Owner: Samhax

import os
import sys
import time
import requests
import argparse
import json
import threading
from typing import List, Dict
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Global constants
API_VERSION = "v19.0"
DEFAULT_ACCESS_TOKEN = "EAA9FWFF6O1gBQD5bT9wvta6qnag6ZBZAj53JZCKHYY9ZAuBr731UKBXCVgZAZCLAzibZAkzZCaF4t1UEFZC298dKVXrpfj2X3zZByyfg25a9hdfxUnGWmPppTRQWrrup4Bg2jCBXJ6BrzK3amhvOBwi20icYj8tr0sNDJeTnn6Ox5i3M5iN9WTVvmI8Pc7nGIGTwZDZD"

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
    """)

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_idx = 0
        self.failed_proxies = set()
        self.lock = threading.Lock()
    
    def load_proxies(self, proxy_file: str):
        """Load proxies from file"""
        try:
            if not os.path.exists(proxy_file):
                print(f"{RED}[-] Proxy file not found: {proxy_file}{RESET}")
                return
            with open(proxy_file, 'r') as f:
                for line in f:
                    proxy = line.strip()
                    if proxy and not proxy.startswith('#'):
                        # Handle format ip:port:user:pass
                        parts = proxy.split(':')
                        if len(parts) == 4:
                            formatted_proxy = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                            self.proxies.append(formatted_proxy)
                        else:
                            self.proxies.append(f"http://{proxy}")
            print(f"{GREEN}[+] Loaded {len(self.proxies)} proxies{RESET}")
        except Exception as e:
            print(f"{RED}[-] Error loading proxies: {e}{RESET}")
    
    def get_next(self) -> Dict:
        """Get next available proxy"""
        if not self.proxies:
            return {}
            
        with self.lock:
            start_idx = self.current_idx
            while True:
                proxy = self.proxies[self.current_idx]
                self.current_idx = (self.current_idx + 1) % len(self.proxies)
                
                if proxy not in self.failed_proxies:
                    # For this tool, we'll return the proxy and let the request fail if it's bad
                    # Testing every proxy on every get_next is too slow
                    return {"http": proxy, "https": proxy}
                
                if self.current_idx == start_idx:
                    break
        
        return {}

class MenuSystem:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.access_token = DEFAULT_ACCESS_TOKEN
        self.phone_numbers = []
        self.options = {
            "1": ("Check Number Status", self.check_number_status),
            "2": ("Report Single Number", self.report_single_number),
            "3": ("Mass Report Numbers", self.mass_report_numbers),
            "4": ("Load Proxies", self.load_proxies_menu),
            "5": ("Load Phone Numbers", self.load_phone_numbers_menu),
            "6": ("Show Settings", self.show_settings),
            "0": ("Exit", self.exit_tool)
        }
    
    def show_menu(self):
        """Display main menu"""
        banner()
        print(f"{BLUE}Available Options:{RESET}")
        for key, (desc, _) in self.options.items():
            print(f"{YELLOW}{key}. {desc}{RESET}")
        print(f"{BLUE}\nEnter option number: {RESET}", end="")
    
    def load_proxies_menu(self):
        """Load proxies from file via menu"""
        proxy_file = input("Enter proxy file path (default: proxiex.txt): ") or "proxiex.txt"
        self.proxy_manager.load_proxies(proxy_file)
        input("\nPress Enter to continue...")
    
    def load_phone_numbers_menu(self):
        """Load phone numbers from file via menu"""
        phone_file = input("Enter phone numbers file path (default: phones.txt): ") or "phones.txt"
        self.load_phone_numbers(phone_file)
        input("\nPress Enter to continue...")

    def load_phone_numbers(self, phone_file: str):
        """Internal method to load phone numbers"""
        try:
            if not os.path.exists(phone_file):
                print(f"{RED}[-] Phone file not found: {phone_file}{RESET}")
                return
            with open(phone_file, 'r') as f:
                self.phone_numbers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"{GREEN}[+] Loaded {len(self.phone_numbers)} phone numbers{RESET}")
        except Exception as e:
            print(f"{RED}[-] Error loading phone numbers: {e}{RESET}")
    
    def show_settings(self):
        """Show current settings"""
        banner()
        print(f"{BLUE}Current Settings:{RESET}")
        print(f"Access Token: {self.access_token[:10]}..." if self.access_token else "Not set")
        print(f"Proxies: {len(self.proxy_manager.proxies)} loaded")
        print(f"Phone Numbers: {len(self.phone_numbers)} loaded")
        input("\nPress Enter to continue...")
    
    def check_number_status(self):
        """Check status of single number"""
        phone_id = input("Enter phone number ID: ")
        if not phone_id:
            print(f"{RED}[-] Phone number required{RESET}")
            return
            
        status = self._check_number_status(phone_id)
        if "error" in status:
            print(f"{RED}[-] Error: {status['error']}{RESET}")
        else:
            print(f"\nStatus: {status.get('status', 'Unknown')}")
            print(f"Message: {status.get('message', 'N/A')}")
        input("\nPress Enter to continue...")
    
    def _check_number_status(self, phone_id: str) -> Dict:
        """Internal method to check number status"""
        url = f"https://graph.facebook.com/{API_VERSION}/{phone_id}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            proxy = self.proxy_manager.get_next()
            response = requests.get(
                url,
                headers=headers,
                proxies=proxy if proxy else None,
                timeout=10
            )
            
            data = response.json()
            
            if 'error' in data:
                error_code = data['error'].get('code')
                if error_code == 100:
                    return {"status": "temporary_ban", "message": "Temporary restriction"}
                elif error_code == 102:
                    return {"status": "permanent_ban", "message": "Permanent ban"}
                elif error_code == 103:
                    return {"status": "suspicious_activity", "message": "Suspicious activity detected"}
                return {"status": "error", "message": data['error'].get('message', 'Unknown error')}
                    
            if data.get('status') == 'active':
                return {"status": "active", "message": "Number is active"}
                
            return {"status": "unknown", "message": "Cannot determine status", "raw": data}
        except Exception as e:
            return {"error": str(e)}
    
    def report_single_number(self):
        """Report single number"""
        phone_id = input("Enter phone number ID: ")
        if not phone_id:
            print(f"{RED}[-] Phone number required{RESET}")
            return
            
        result = self._report_number(phone_id)
        print(f"\nResult: {'Success' if result.get('success') else 'Failed'}")
        if result.get('success'):
            print(f"Response: {result.get('response')}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        input("\nPress Enter to continue...")
    
    def mass_report_numbers(self):
        """Mass report numbers with configurable iterations"""
        if not self.phone_numbers:
            print(f"{RED}[-] No phone numbers loaded. Use option 5 first.{RESET}")
            input("\nPress Enter to continue...")
            return
            
        try:
            iterations_input = input("Enter number of iterations (default 5): ")
            iterations = int(iterations_input) if iterations_input else 5
            delay_input = input("Enter delay between requests (seconds, default 1.0): ")
            delay = float(delay_input) if delay_input else 1.0
        except ValueError:
            print(f"{RED}[-] Invalid input. Using defaults.{RESET}")
            iterations = 5
            delay = 1.0
        
        print(f"{BLUE}[+] Starting mass report with {iterations} iterations{RESET}")
        results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(iterations):
                for phone_id in self.phone_numbers:
                    future = executor.submit(self._report_number, phone_id)
                    futures.append((future, phone_id, i+1))
                    time.sleep(delay)
            
            for future, phone_id, iteration in futures:
                try:
                    result = future.result()
                    results.append({**result, "iteration": iteration})
                    status = "Success" if result.get('success') else "Failed"
                    color = GREEN if result.get('success') else RED
                    print(f"{BLUE}[{iteration}/{iterations}]{RESET} Reported {phone_id}: {color}{status}{RESET}")
                except Exception as e:
                    print(f"{RED}[!] Error processing {phone_id}: {e}{RESET}")
        
        with open("report_results.json", "w") as f:
            json.dump(results, f, indent=4)
        print(f"{GREEN}[+] Results saved to report_results.json{RESET}")
        input("\nPress Enter to continue...")
    
    def _report_number(self, phone_id: str) -> Dict:
        """Internal method to report number"""
        url = f"https://graph.facebook.com/{API_VERSION}/{phone_id}/report"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "reason": "spam",
            "description": "Samhax BAN TOOL - Spam detection"
        }
        
        try:
            proxy = self.proxy_manager.get_next()
            response = requests.post(
                url,
                headers=headers,
                json=data,
                proxies=proxy if proxy else None,
                timeout=10
            )
            
            return {
                "phone_id": phone_id,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                "phone_id": phone_id,
                "error": str(e)
            }
    
    def exit_tool(self):
        """Exit tool"""
        print(f"{GREEN}[+] Thank you for using rD4DDY SAMHAX BAN TOOL{RESET}")
        sys.exit(0)
    
    def run(self):
        """Main menu loop"""
        # Auto-load default files if they exist
        if os.path.exists("proxiex.txt"):
            self.proxy_manager.load_proxies("proxiex.txt")
        if os.path.exists("phones.txt"):
            self.load_phone_numbers("phones.txt")
            
        while True:
            try:
                self.show_menu()
                choice = input().strip()
                
                if choice in self.options:
                    _, func = self.options[choice]
                    func()
                else:
                    print(f"{RED}[-] Invalid option{RESET}")
                    time.sleep(1)
            except KeyboardInterrupt:
                self.exit_tool()
            except Exception as e:
                print(f"{RED}[-] An unexpected error occurred: {e}{RESET}")
                time.sleep(2)

if __name__ == "__main__":
    menu = MenuSystem()
    menu.run()
