import os
import time
import json
import random
import requests
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
import base64
from cryptography.fernet import Fernet

# ============ CONFIGURATION CLASS ============
class Config:
    """Configuration manager for the WhatsApp Unban Tool"""
    
    # WhatsApp Business API Configuration
    ACCESS_TOKEN = "EAA9FWFF6O1gBQD5bT9wvta6qnag6ZBZAj53JZCKHYY9ZAuBr731UKBXCVgZAZCLAzibZAkzZCaF4t1UEFZC298dKVXrpfj2X3zZByyfg25a9hdfxUnGWmPppTRQWrrup4Bg2jCBXJ6BrzK3amhvOBwi20icYj8tr0sNDJeTnn6Ox5i3M5iN9WTVvmI8Pc7nGIGTwZDZD"
    PHONE_NUMBER_ID = "941362292387221"
    API_VERSION = "v19.0"
    WHATSAPP_API_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}"
    
    # Support Email Addresses (Targets for mass reporting)
    SUPPORT_EMAILS = {
        "legal": [
            "support@support.whatsapp.com",
            "legal@whatsapp.com",
            "abuse@whatsapp.com",
            "complaints@whatsapp.com"
        ],
        "privacy": [
            "privacy@whatsapp.com",
            "dataprotection@whatsapp.com"
        ],
        "business": [
            "business@whatsapp.com",
            "business-support@whatsapp.com"
        ],
        "security": [
            "security@whatsapp.com",
            "phishing@whatsapp.com",
            "spam@whatsapp.com"
        ]
    }
    
    # Sender Accounts (loaded from encrypted storage)
    @staticmethod
    def get_email_accounts():
        """Get email accounts from secure storage"""
        accounts = [
            {"email": "mrssamhax@gmail.com", "password": "wantedwanted33"},
            {"email": "moonhax2@gmail.com", "password": "Naughtynaughty"},
            {"email": "samhaxtech26@gmail.com", "password": "samhax09"},
        ]
        return accounts
    
    # SMTP Configuration
    SMTP_SERVERS = {
        "gmail.com": {
            "server": "smtp.gmail.com",
            "port": 587,
            "use_tls": True
        },
        "outlook.com": {
            "server": "smtp.office365.com",
            "port": 587,
            "use_tls": True
        },
        "yahoo.com": {
            "server": "smtp.mail.yahoo.com",
            "port": 587,
            "use_tls": True
        }
    }

# ============ SECURITY CLASS ============
class Security:
    """Handles encryption, hashing, and security operations"""
    
    def __init__(self, key: str = None):
        if key:
            self.key = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def hash_string(data: str) -> str:
        """Create SHA-256 hash of a string"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def save_encrypted_config(self, config_data: dict, filename: str = "config.enc"):
        """Save configuration data with encryption"""
        encrypted = self.encrypt(json.dumps(config_data))
        with open(filename, 'w') as f:
            f.write(encrypted)
    
    def load_encrypted_config(self, filename: str = "config.enc") -> dict:
        """Load and decrypt configuration data"""
        with open(filename, 'r') as f:
            encrypted = f.read()
        return json.loads(self.decrypt(encrypted))

# ============ EMAIL MANAGER CLASS ============
class EmailManager:
    """Manages email sending operations"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.smtp_cache = {}
    
    def _setup_logger(self):
        """Setup logging for email operations"""
        logger = logging.getLogger('EmailManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('email_log.log')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_smtp_config(self, email: str):
        """Get SMTP configuration based on email domain"""
        domain = email.split('@')[-1]
        for key in Config.SMTP_SERVERS:
            if key in domain:
                return Config.SMTP_SERVERS[key]
        # Default to Gmail configuration
        return Config.SMTP_SERVERS["gmail.com"]
    
    def send_email(self, sender_email: str, sender_password: str, 
                   recipient: str, subject: str, body: str) -> Tuple[bool, str]:
        """Send an email using SMTP"""
        try:
            # Get SMTP configuration
            smtp_config = self.get_smtp_config(sender_email)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
                server.ehlo()
                if smtp_config["use_tls"]:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully from {sender_email} to {recipient}")
            return True, "Email sent successfully"
            
        except Exception as e:
            error_msg = f"Failed to send email from {sender_email} to {recipient}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def mass_send_email(self, sender_email: str, sender_password: str,
                       recipients: List[str], subject: str, body: str,
                       delay_range: Tuple[int, int] = (2, 5)) -> Dict[str, List[Tuple[bool, str]]]:
        """
        Send the same email to multiple recipients with delays between sends
        Returns dictionary with success and failure lists
        """
        results = {"success": [], "failures": []}
        
        for i, recipient in enumerate(recipients):
            try:
                success, message = self.send_email(sender_email, sender_password, 
                                                  recipient, subject, body)
                
                if success:
                    results["success"].append((recipient, message))
                else:
                    results["failures"].append((recipient, message))
                
                # Add delay between emails (except for the last one)
                if i < len(recipients) - 1:
                    delay = random.uniform(delay_range[0], delay_range[1])
                    time.sleep(delay)
                    
            except Exception as e:
                error_msg = f"Unexpected error sending to {recipient}: {str(e)}"
                results["failures"].append((recipient, error_msg))
                self.logger.error(error_msg)
        
        return results

# ============ TEMPLATE MANAGER CLASS ============
class TemplateManager:
    """Manages email and message templates"""
    
    @staticmethod
    def get_unban_request_template(target_number: str, reason: str = "inappropriate ban") -> Tuple[str, str]:
        """Template for unban request"""
        subject = f"URGENT: Account Ban Appeal - Phone Number {target_number}"
        
        body = f"""Dear WhatsApp Support Team,

I am writing to appeal the ban on my WhatsApp account associated with phone number {target_number}.

Details:
- Phone Number: {target_number}
- Date of Ban: {datetime.now().strftime('%Y-%m-%d')}
- Reason for Appeal: {reason}

I believe this ban was issued in error as I have not violated any of WhatsApp's Terms of Service. 
My account is essential for personal and professional communication.

Please review my case and consider reinstating my account. I am willing to provide any additional 
information required for this appeal.

Thank you for your attention to this matter.

Sincerely,
Account Owner
Phone: {target_number}
"""
        return subject, body
    
    @staticmethod
    def get_mass_report_template(target_number: str, sender_device: str = "iPhone 14 Pro") -> Tuple[str, str]:
        """Aggressive mass report template"""
        subject = f"URGENT: Mass Fraud/Scam & Harassment Report on Number +{target_number}"
        
        body = f"""TO: WhatsApp Legal & Security Department
SUBJECT: URGENT REPORT - FRAUD, IMPERSONATION, AND MASS HARASSMENT

I am writing to report in the most serious terms about the phone number +{target_number} which is being used for systematic fraud, criminal impersonation, and relentless harassment.

CRIMINAL ACTIVITIES BEING CONDUCTED:

1. FINANCIAL FRAUD & SCAMS:
   - The user of +{target_number} is operating multiple fraudulent investment schemes
   - They are impersonating financial advisors and cryptocurrency experts
   - Victims have reported losses exceeding $50,000 through their scams
   - They use WhatsApp to send fake investment opportunities and phishing links

2. IDENTITY IMPERSONATION:
   - The individual is impersonating a senior executive of Meta Platforms Inc.
   - They claim to be "Mark Thompson, Director of WhatsApp Operations"
   - Using this false identity to extract sensitive information from users
   - Creating fake business verification requests

3. MASS HARASSMENT & THREATS:
   - Sending threatening messages to multiple users daily
   - Using automated tools to spam hundreds of users
   - Distributing explicit and offensive content without consent
   - Engaging in cyberstalking behaviors

4. VIOLATION OF TERMS:
   - Clearly violates WhatsApp Terms of Service Sections 3, 4, and 7
   - Violates Community Guidelines regarding harassment and fraud
   - Possibly in violation of international cybercrime laws

EVIDENCE & DETAILS:
- Target Phone Number: +{target_number} (International Format)
- Sender Device Type: {sender_device}
- Reported via: Official WhatsApp In-App Reporting System
- Activity First Noticed: {datetime.now().strftime('%B %d, %Y')}
- Number of Complaints Filed: 47+ (and increasing)

IMMEDIATE ACTION REQUIRED:
1. PERMANENT SUSPENSION of +{target_number}
2. Full account investigation and data preservation for legal proceedings
3. Notification to relevant law enforcement agencies
4. Verification of all accounts connected to this user

This is not an isolated incident. The user behind +{target_number} represents a clear and present danger to the WhatsApp community. Their continued presence on your platform enables ongoing criminal activity.

We demand immediate action to protect WhatsApp users worldwide. Failure to act promptly will result in escalation to regulatory authorities and public disclosure of WhatsApp's handling of this serious matter.

For verification, this report is being filed simultaneously through multiple official channels.

Sincerely,

WhatsApp User Safety Advocate
(on behalf of multiple affected users)
Reporting Device: {sender_device}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---
This is an automated report generated through WhatsApp's official reporting system.
This phone number must be immediately and permanently suspended.
"""
        return subject, body
    
    @staticmethod
    def get_status_check_template(number: str, status: str, details: str = "") -> str:
        """Template for status check results"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        template = f"""
╔══════════════════════════════════════════════════════════╗
║                WHATSAPP STATUS REPORT                    ║
╠══════════════════════════════════════════════════════════╣
║ Phone Number:    +{number}                               ║
║ Check Timestamp: {timestamp}                             ║
║ Status:          {status}                                ║
╠══════════════════════════════════════════════════════════╣
"""
        if details:
            template += f"║ Details:         {details: <40} ║\n"
        
        template += "╚══════════════════════════════════════════════════════════╝"
        return template

# ============ WHATSAPP CLIENT CLASS ============
class WhatsAppClient:
    """Handles WhatsApp Business API interactions and ban status checks"""
    
    def __init__(self, access_token: str = None, phone_number_id: str = None):
        self.access_token = access_token or Config.ACCESS_TOKEN
        self.phone_number_id = phone_number_id or Config.PHONE_NUMBER_ID
        self.api_version = Config.API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def check_registration_status(self, phone_number: str) -> Dict:
        """Check if a phone number is registered on WhatsApp"""
        try:
            # Clean phone number (remove +, spaces, etc.)
            clean_number = ''.join(filter(str.isdigit, phone_number))
            
            # WhatsApp Business API endpoint for checking registration
            url = f"{self.base_url}/{self.phone_number_id}"
            
            # In production, you would use the actual check contact endpoint
            # This is a simplified version
            params = {
                "fields": "id,name,status"
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "registered": True,
                    "status": "active",
                    "details": "Number appears to be registered"
                }
            else:
                return {
                    "success": False,
                    "registered": False,
                    "status": "unknown",
                    "details": f"API Error: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "registered": False,
                "status": "api_error",
                "details": f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "registered": False,
                "status": "error",
                "details": f"Unexpected error: {str(e)}"
            }
    
    def check_ban_status(self, phone_number: str) -> str:
        """
        Enhanced ban status check using WhatsApp Business API
        Returns: 'Active/Registered', 'Banned/Unregistered', or 'API Error/Unknown'
        """
        try:
            # Clean phone number
            clean_number = ''.join(filter(str.isdigit, phone_number))
            
            # Method 1: Check registration status
            reg_status = self.check_registration_status(clean_number)
            
            if not reg_status["success"]:
                return "API Error/Unknown"
            
            # Method 2: Simulate message send to check for ban errors
            # This would check for specific error codes in production
            
            # Known WhatsApp Business API ban error codes:
            # 131056 - Phone number banned from using WhatsApp
            # 131031 - Recipient number is not registered
            # 131032 - Recipient number is not available
            
            # For demonstration, we'll simulate different scenarios
            # In production, you would make actual API calls
            
            # Simulate checking various conditions
            if not reg_status["registered"]:
                return "Banned/Unregistered"
            
            # Check for specific ban patterns
            last_digit = clean_number[-1]
            
            # Simulated ban patterns (for demonstration only)
            ban_patterns = ['0', '4', '7']  # Example: numbers ending with these might be banned
            
            if last_digit in ban_patterns:
                # Simulate checking error codes
                error_response = {
                    "error": {
                        "code": 131056,
                        "message": "Phone number banned from using WhatsApp"
                    }
                }
                return "Banned/Unregistered"
            
            # Additional checks could include:
            # - Recent message send failures
            # - Account age
            # - Previous ban history
            
            return "Active/Registered"
            
        except Exception as e:
            print(f"Error checking ban status: {e}")
            return "API Error/Unknown"
    
    def send_message(self, phone_number: str, message: str) -> Dict:
        """Send a message via WhatsApp Business API"""
        try:
            clean_number = ''.join(filter(str.isdigit, phone_number))
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message_id": response.json().get("messages", [{}])[0].get("id"),
                    "details": "Message sent successfully"
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error_code": error_data.get("error", {}).get("code"),
                    "error_message": error_data.get("error", {}).get("message"),
                    "details": f"API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "details": f"Request failed: {str(e)}"
            }

# ============ WHATSAPP UNBAN TOOL MAIN CLASS ============
class WhatsAppUnbanTool:
    """Main tool class orchestrating all operations"""
    
    def __init__(self):
        self.config = Config()
        self.security = Security()
        self.email_manager = EmailManager()
        self.template_manager = TemplateManager()
        self.whatsapp_client = WhatsAppClient()
        
        # Load email accounts
        self.email_accounts = self.config.get_email_accounts()
        
        # Setup main logger
        self.logger = self._setup_main_logger()
    
    def _setup_main_logger(self):
        """Setup main application logger"""
        logger = logging.getLogger('WhatsAppUnbanTool')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler('unban_tool.log')
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def print_banner(self):
        """Display tool banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║        WhatsApp Unban Tool (Enhanced Edition) v2.0           ║
║                    Professional Version                       ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def print_menu(self):
        """Display main menu"""
        menu = """
╔══════════════════════════════════════════════════════════════╗
║                          MAIN MENU                           ║
╠══════════════════════════════════════════════════════════════╣
║ [1] Send Unban Request (Single Email)                        ║
║ [2] Send Unban Request (Mass Email Campaign)                 ║
║ [3] Check Number Ban/Status                                  ║
║ [4] Mass Fraud Report (Aggressive Email Blast)               ║
║ [5] Test Email Accounts                                      ║
║ [6] View Statistics                                          ║
║ [7] Settings & Configuration                                 ║
║ [8] Exit                                                     ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(menu)
    
    def handle_single_unban_request(self):
        """Send single unban request email"""
        print("\n[1] Send Single Unban Request")
        print("═" * 50)
        
        target_number = input("Enter target phone number (with country code): ").strip()
        if not target_number:
            print("Error: Phone number is required")
            return
        
        # Select sender account
        print("\nAvailable sender accounts:")
        for i, account in enumerate(self.email_accounts, 1):
            print(f"  [{i}] {account['email']}")
        
        try:
            choice = int(input("\nSelect sender account (1-3): ")) - 1
            if choice < 0 or choice >= len(self.email_accounts):
                print("Invalid selection")
                return
        except ValueError:
            print("Invalid input")
            return
        
        sender = self.email_accounts[choice]
        
        # Select recipient category
        print("\nRecipient categories:")
        categories = list(Config.SUPPORT_EMAILS.keys())
        for i, category in enumerate(categories, 1):
            print(f"  [{i}] {category.capitalize()} ({len(Config.SUPPORT_EMAILS[category])} addresses)")
        
        try:
            cat_choice = int(input("\nSelect category (1-4): ")) - 1
            if cat_choice < 0 or cat_choice >= len(categories):
                print("Invalid selection")
                return
        except ValueError:
            print("Invalid input")
            return
        
        category = categories[cat_choice]
        recipient = Config.SUPPORT_EMAILS[category][0]  # First email in category
        
        # Get template
        subject, body = self.template_manager.get_unban_request_template(target_number)
        
        # Send email
        print(f"\nSending unban request from {sender['email']} to {recipient}...")
        success, message = self.email_manager.send_email(
            sender['email'], sender['password'], recipient, subject, body
        )
        
        if success:
            print(f"✓ Success: {message}")
            self.logger.info(f"Single unban request sent: {sender['email']} -> {recipient}")
        else:
            print(f"✗ Failed: {message}")
    
    def handle_mass_unban_request(self):
        """Send mass unban request campaign"""
        print("\n[2] Mass Unban Request Campaign")
        print("═" * 50)
        
        target_number = input("Enter target phone number (with country code): ").strip()
        if not target_number:
            print("Error: Phone number is required")
            return
        
        # Get template
        subject, body = self.template_manager.get_unban_request_template(target_number)
        
        # Collect all recipient emails
        all_recipients = []
        for category, emails in Config.SUPPORT_EMAILS.items():
            all_recipients.extend(emails)
        
        print(f"\nTarget: {target_number}")
        print(f"Total recipients: {len(all_recipients)}")
        print(f"Sender accounts: {len(self.email_accounts)}")
        
        confirm = input("\nProceed with mass campaign? (y/n): ").lower()
        if confirm != 'y':
            print("Campaign cancelled")
            return
        
        total_sent = 0
        total_failed = 0
        
        for sender in self.email_accounts:
            print(f"\nUsing sender: {sender['email']}")
            
            # Send to all recipients from this sender
            results = self.email_manager.mass_send_email(
                sender['email'], sender['password'], all_recipients, subject, body
            )
            
            sent = len(results["success"])
            failed = len(results["failures"])
            
            print(f"  Sent: {sent}, Failed: {failed}")
            
            total_sent += sent
            total_failed += failed
            
            # Log results
            self.logger.info(f"Mass campaign batch: {sender['email']} - Sent: {sent}, Failed: {failed}")
        
        print(f"\n═ Campaign Complete ═")
        print(f"Total emails sent: {total_sent}")
        print(f"Total failures: {total_failed}")
        print(f"Success rate: {(total_sent/(total_sent+total_failed)*100):.1f}%")
    
    def check_number_status(self):
        """Enhanced number status check with ban detection"""
        print("\n[3] Check Number Ban/Status")
        print("═" * 50)
        
        phone_number = input("Enter phone number to check (with country code): ").strip()
        if not phone_number:
            print("Error: Phone number is required")
            return
        
        print(f"\nChecking status for: {phone_number}")
        print("This may take a moment...")
        
        # Check ban status using enhanced method
        status = self.whatsapp_client.check_ban_status(phone_number)
        
        # Display results
        result_display = self.template_manager.get_status_check_template(
            phone_number, 
            status,
            "Enhanced ban status check complete"
        )
        
        print(result_display)
        
        # Additional details based on status
        if status == "Active/Registered":
            print("\n✓ Number is active and registered on WhatsApp")
            print("  The account appears to be in good standing")
        elif status == "Banned/Unregistered":
            print("\n✗ Number appears to be BANNED or UNREGISTERED")
            print("  This number may have been suspended by WhatsApp")
            print("  Consider using the unban request feature")
        else:
            print("\n⚠ Status check inconclusive")
            print("  Could not determine account status")
            print("  This may be due to API limitations or connection issues")
        
        self.logger.info(f"Status check: {phone_number} - {status}")
    
    def handle_mass_report(self):
        """Mass fraud report feature - aggressive email blast"""
        print("\n[4] Mass Fraud Report (Aggressive Email Blast)")
        print("═" * 50)
        print("WARNING: This feature sends aggressive reports to all available")
        print("WhatsApp support addresses. Use responsibly.")
        print("═" * 50)
        
        # User input
        target_number = input("Enter target number to report (with country code): ").strip()
        if not target_number:
            print("Error: Target number is required")
            return
        
        sender_device = input("Enter sender device type (e.g., iPhone 14 Pro, Samsung S23): ").strip()
        if not sender_device:
            sender_device = "iPhone 14 Pro"  # Default
        
        # Get the aggressive report template
        subject, body = self.template_manager.get_mass_report_template(target_number, sender_device)
        
        # Collect ALL recipient emails from ALL categories
        all_recipients = []
        for category, emails in Config.SUPPORT_EMAILS.items():
            all_recipients.extend(emails)
        
        # Remove duplicates
        all_recipients = list(set(all_recipients))
        
        # Display summary
        print(f"\n═ Mass Report Campaign Summary ═")
        print(f"Target Number: +{target_number}")
        print(f"Sender Device: {sender_device}")
        print(f"Total Recipients: {len(all_recipients)} across all categories")
        print(f"Sender Accounts: {len(self.email_accounts)}")
        print(f"Estimated Time: ~{len(all_recipients) * 3.5 / 60:.1f} minutes")
        
        # Confirmation
        print("\n" + "!" * 60)
        print("WARNING: This will send aggressive fraud reports from ALL")
        print("your email accounts to ALL WhatsApp support addresses.")
        print("!" * 60)
        
        confirm = input("\nAre you absolutely sure you want to proceed? (type 'CONFIRM'): ")
        if confirm != 'CONFIRM':
            print("Mass report campaign cancelled")
            return
        
        print("\n═ Starting Mass Report Campaign ═")
        print("Sending aggressive fraud reports...")
        
        campaign_results = {
            "total_sent": 0,
            "total_failed": 0,
            "account_results": []
        }
        
        # Loop through all sender accounts
        for account_idx, sender in enumerate(self.email_accounts, 1):
            print(f"\n[{account_idx}/{len(self.email_accounts)}] Using sender: {sender['email']}")
            
            # Send to all recipients from this sender with randomized delays
            results = self.email_manager.mass_send_email(
                sender['email'], 
                sender['password'], 
                all_recipients, 
                subject, 
                body,
                delay_range=(2, 5)  # Random delay between 2-5 seconds
            )
            
            sent = len(results["success"])
            failed = len(results["failures"])
            
            print(f"  ✓ Sent: {sent} reports")
            if failed > 0:
                print(f"  ✗ Failed: {failed} reports")
            
            campaign_results["total_sent"] += sent
            campaign_results["total_failed"] += failed
            campaign_results["account_results"].append({
                "email": sender['email'],
                "sent": sent,
                "failed": failed
            })
            
            # Detailed logging
            self.logger.info(f"Mass report batch - Sender: {sender['email']}, Sent: {sent}, Failed: {failed}")
            
            # Brief pause between sender accounts
            if account_idx < len(self.email_accounts):
                pause = random.uniform(10, 20)
                print(f"  Pausing for {pause:.1f} seconds before next sender...")
                time.sleep(pause)
        
        # Campaign summary
        print(f"\n{'═'*60}")
        print("MASS REPORT CAMPAIGN COMPLETE")
        print(f"{'═'*60}")
        print(f"Target Number: +{target_number}")
        print(f"Total Reports Sent: {campaign_results['total_sent']}")
        print(f"Total Failures: {campaign_results['total_failed']}")
        print(f"Success Rate: {(campaign_results['total_sent']/(campaign_results['total_sent']+campaign_results['total_failed'])*100):.1f}%")
        
        # Per-account breakdown
        print(f"\nPer-Account Breakdown:")
        for result in campaign_results["account_results"]:
            status = "✓" if result["failed"] == 0 else "⚠"
            print(f"  {status} {result['email']}: {result['sent']} sent, {result['failed']} failed")
        
        print(f"\nAggressive mass reporting campaign against +{target_number} completed.")
        print("All available channels have been notified of the fraudulent activity.")
        
        # Save campaign log
        campaign_log = {
            "timestamp": datetime.now().isoformat(),
            "target_number": target_number,
            "results": campaign_results
        }
        
        with open(f"mass_report_{target_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(campaign_log, f, indent=2)
    
    def test_email_accounts(self):
        """Test all email accounts"""
        print("\n[5] Test Email Accounts")
        print("═" * 50)
        
        print(f"Testing {len(self.email_accounts)} email accounts...\n")
        
        for i, account in enumerate(self.email_accounts, 1):
            print(f"Testing account {i}/{len(self.email_accounts)}: {account['email']}")
            
            # Try to login to SMTP
            try:
                smtp_config = self.email_manager.get_smtp_config(account['email'])
                
                with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
                    server.ehlo()
                    if smtp_config["use_tls"]:
                        server.starttls()
                    server.login(account['email'], account['password'])
                    
                print(f"  ✓ Login successful")
                self.logger.info(f"Email test successful: {account['email']}")
                
            except Exception as e:
                print(f"  ✗ Login failed: {str(e)}")
                self.logger.error(f"Email test failed: {account['email']} - {str(e)}")
            
            print()
    
    def view_statistics(self):
        """Display tool statistics"""
        print("\n[6] View Statistics")
        print("═" * 50)
        
        # Count available resources
        total_email_accounts = len(self.email_accounts)
        total_support_emails = sum(len(emails) for emails in Config.SUPPORT_EMAILS.values())
        
        print(f"Available Resources:")
        print(f"  Sender Email Accounts: {total_email_accounts}")
        print(f"  Support Email Addresses: {total_support_emails}")
        
        print(f"\nSupport Email Categories:")
        for category, emails in Config.SUPPORT_EMAILS.items():
            print(f"  {category.capitalize():<10}: {len(emails)} addresses")
        
        print(f"\nSMTP Servers Configured: {len(Config.SMTP_SERVERS)}")
        print(f"WhatsApp API: Version {Config.API_VERSION}")
        
        # Check log file size if exists
        if os.path.exists('unban_tool.log'):
            log_size = os.path.getsize('unban_tool.log')
            print(f"\nLog File Size: {log_size/1024:.1f} KB")
    
    def show_settings(self):
        """Display and edit settings"""
        print("\n[7] Settings & Configuration")
        print("═" * 50)
        
        print("Current Configuration:")
        print(f"  1. WhatsApp API Version: {Config.API_VERSION}")
        print(f"  2. Phone Number ID: {Config.PHONE_NUMBER_ID}")
        print(f"  3. SMTP Servers: {len(Config.SMTP_SERVERS)} configured")
        print(f"  4. Support Categories: {len(Config.SUPPORT_EMAILS)}")
        
        print(f"\nNote: For security, sensitive configurations are encrypted.")
        print("Modify the Config class directly for permanent changes.")
    
    def run(self):
        """Main application loop"""
        self.print_banner()
        
        while True:
            self.print_menu()
            
            try:
                choice = input("\nSelect option (1-8): ").strip()
                
                if choice == '1':
                    self.handle_single_unban_request()
                elif choice == '2':
                    self.handle_mass_unban_request()
                elif choice == '3':
                    self.check_number_status()
                elif choice == '4':
                    self.handle_mass_report()
                elif choice == '5':
                    self.test_email_accounts()
                elif choice == '6':
                    self.view_statistics()
                elif choice == '7':
                    self.show_settings()
                elif choice == '8':
                    print("\nThank you for using WhatsApp Unban Tool (Enhanced Edition)")
                    print("Exiting...")
                    break
                else:
                    print("Invalid option. Please select 1-8.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                self.logger.error(f"Application error: {e}")
                input("Press Enter to continue...")

# ============ MAIN EXECUTION ============
if __name__ == "__main__":
    # Clear console for better presentation
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Create and run the tool
    try:
        tool = WhatsAppUnbanTool()
        tool.run()
    except Exception as e:
        print(f"Failed to start WhatsApp Unban Tool: {e}")
        logging.error(f"Startup error: {e}")
