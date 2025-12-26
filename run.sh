#!/bin/bash
echo "[+] Starting rD4DDY SAMHAX B4N TOOL..."
echo "[*] Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[-] Python3 not found. Installing..."
    pkg install python
fi

# Check requests module
if ! python3 -c "import requests" &> /dev/null; then
    echo "[-] Requests module not found. Installing..."
    pip install requests
fi

# Check proxy file exists
if [ ! -f "proxies.txt" ]; then
    echo "[!] Creating proxy file..."
    echo "# Add proxies here" > proxies.txt
    echo "http://proxy1:port" >> proxies.txt
    echo "http://proxy2:port" >> proxies.txt
fi

# Check phone numbers file exists
if [ ! -f "phones.txt" ]; then
    echo "[!] Creating phone numbers file..."
    echo "# Add phone numbers here" > phones.txt
    echo "+1234567890" >> phones.txt
    echo "+9876543210" >> phones.txt
fi

echo "[+] Starting main tool..."
python3 spam.py "$@"
