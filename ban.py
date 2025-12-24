#!/usr/bin/env python3
import time
import argparse
import os
import json
import random
import signal
import sys
from datetime import datetime
import threading

# Offensive message list
OFFENSIVE_MESSAGES = [
    "KUMAIL TERI MAA KI CHUT",
    "KUMAIL TERI RANDI MAA KA BHOSDA",
    "KUMAIL KI MAA DA KALA FUDDA",
    "KUMAIL KISI GASHTI HUN DAYA TERI MAA DA FUDDA",
    "KUMAIL KI MAA KA FUDDA SCUCESSFULLY PASTE",
    "DELIVERY BOY KUMAIL KI MAA KO CHOD K GHORI BNA DUN",
    "KUMAIL KI RANDI MAA KO CHUD CHUD K GASHTI BNA DUN",
    "KUMAIL KI LOADER BAJI KI MAAA KI CHUT",
    "KUMAIL DI PENN DA BHOSDA",
    "KUMAIL TERI MAA RANDI KO QABAR MAI CHODUN"
]

class WhatsAppConnection:
    """Handles WhatsApp connection and messaging"""
    
    def __init__(self):
        self.connected = False
        self.token = None
        
    def connect(self, phone_number):
        """Connect to WhatsApp using phone number"""
        print(f"Connecting to WhatsApp using number: {phone_number}")
        # Simulate connection process
        time.sleep(1)
        self.connected = True
        self.token = f"session_{phone_number}_token"
        print(f"Connected successfully! Token: {self.token}")
        return True
        
    def send_message(self, recipient, message):
        """Send message through WhatsApp connection"""
        if not self.connected:
            print("Not connected to WhatsApp!")
            return False
            
        print(f"Sending '{message}' to {recipient} via {self.token}")
        # Simulate message sending
        time.sleep(0.5)
        return True
        
    def disconnect(self):
        """Disconnect from WhatsApp"""
        self.connected = False
        self.token = None
        print("Disconnected from WhatsApp")


class WhatsAppGroupSpammer:
    def __init__(self, config_file="group_spam_config.json"):
        self.config_file = config_file
        self.load_config()
        self.running = False
        self.connection = WhatsAppConnection()
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "phone_number": "+1234567890",  # Default phone number
            "groups": [
                {"id": "120363424498594173", "type": "group"},
                {"id": "39681437773989@lid", "type": "chat"}
            ],
            "schedule": {
                "delay": 30,
                "repeating": True,
                "interval": 3600,
                "random_messages": False,
                "max_messages": 100
            },
            "history": []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                print("Invalid config file, using defaults")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
            
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def set_phone_number(self, phone_number):
        """Set the phone number to use for connection"""
        self.config["phone_number"] = phone_number
        self.save_config()
        print(f"Phone number set to: {phone_number}")
        
    def set_schedule(self, delay=None, repeating=None, interval=None, 
                     random_messages=None, max_messages=None):
        """Configure sending schedule"""
        if delay is not None:
            self.config["schedule"]["delay"] = delay
        if repeating is not None:
            self.config["schedule"]["repeating"] = repeating
        if interval is not None:
            self.config["schedule"]["interval"] = interval
        if random_messages is not None:
            self.config["schedule"]["random_messages"] = random_messages
        if max_messages is not None:
            self.config["schedule"]["max_messages"] = max_messages
            
        self.save_config()
        print(f"Schedule updated: Delay={delay}, Repeating={repeating}, "
              f"Interval={interval}, Random={random_messages}, Max={max_messages}")
        
    def stop_spam(self):
        """Stop the spamming process"""
        self.running = False
        print("\nStopping spamming...")
        
    def start_spam(self):
        """Start the spamming process"""
        if not self.config["groups"]:
            print("No groups configured!")
            return
            
        print(f"Starting group spam bot with {len(self.config['groups'])} targets")
        print(f"Using phone number: {self.config['phone_number']}")
        print(f"Delay: {self.config['schedule']['delay']} seconds")
        print(f"Repeating: {self.config['schedule']['repeating']}")
        print(f"Random messages: {self.config['schedule']['random_messages']}")
        print(f"Max messages per target: {self.config['schedule']['max_messages']}")
        
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: self.stop_spam())
        
        # Connect to WhatsApp
        print("\nConnecting to WhatsApp...")
        if not self.connection.connect(self.config["phone_number"]):
            print("Failed to connect to WhatsApp!")
            return
            
        self.running = True
        message_count = 0
        
        while self.running:
            for target in self.config["groups"]:
                if message_count >= self.config["schedule"]["max_messages"]:
                    print(f"Max messages ({self.config['schedule']['max_messages']}) reached, stopping")
                    self.stop_spam()
                    break
                    
                # Select message based on random setting
                if self.config["schedule"]["random_messages"]:
                    message = random.choice(OFFENSIVE_MESSAGES)
                else:
                    # Cycle through messages
                    message_index = len(self.config["history"]) % len(OFFENSIVE_MESSAGES)
                    message = OFFENSIVE_MESSAGES[message_index]
                    
                print(f"\nSending to {target['type']} {target['id']}: {message}")
                if not self.connection.send_message(target["id"], message):
                    print("Failed to send message, continuing...")
                    continue
                    
                # Update history
                self.config["history"].append({
                    "message": message,
                    "target_id": target["id"],
                    "target_type": target["type"],
                    "timestamp": datetime.now().isoformat()
                })
                message_count += 1
                
            # Check if we should stop
            if not self.config["schedule"]["repeating"]:
                break
                
            # Wait for next cycle
            print(f"\nWaiting {self.config['schedule']['interval']} seconds...")
            time.sleep(self.config["schedule"]["interval"])
            
        # Disconnect from WhatsApp
        self.connection.disconnect()
        print("Spamming completed")

def main():
    parser = argparse.ArgumentParser(description='WhatsApp Group Spammer')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Set phone number command
    phone_parser = subparsers.add_parser('phone', help='Set phone number')
    phone_parser.add_argument('phone_number', help='Your WhatsApp phone number')
    
    # Set schedule command
    sched_parser = subparsers.add_parser('schedule', help='Set spam schedule')
    sched_parser.add_argument('--delay', type=int, default=30, help='Delay between messages (seconds)')
    sched_parser.add_argument('--no-repeat', action='store_true', help='Don\'t repeat')
    sched_parser.add_argument('--interval', type=int, default=3600, help='Interval between cycles (seconds)')
    sched_parser.add_argument('--random', action='store_true', help='Send random messages')
    sched_parser.add_argument('--max-messages', type=int, default=100, help='Maximum messages per target')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start spamming')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop spamming')
    
    args = parser.parse_args()
    spammer = WhatsAppGroupSpammer()
    
    if args.command == 'phone':
        spammer.set_phone_number(args.phone_number)
    elif args.command == 'schedule':
        spammer.set_schedule(
            delay=args.delay,
            repeating=not args.no_repeat,
            interval=args.interval,
            random_messages=args.random,
            max_messages=args.max_messages
        )
    elif args.command == 'start':
        spammer.start_spam()
    elif args.command == 'stop':
        spammer.stop_spam()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
