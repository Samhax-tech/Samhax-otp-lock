#!/bin/bash
echo "[+] Starting rD4DDY SAMHAX BAN TOOL..."
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
    echo "142.111.48.253:7030:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "31.59.20.176:6754:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "23.95.150.145:6114:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "198.23.239.134:6540:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "107.172.163.27:6543:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "198.105.121.200:6462:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "64.137.96.74:6641:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "84.247.60.125:6095:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "216.10.27.159:6837:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
    echo "142.111.67.146:5611:ihdlyccz:vwyehnt1tqhs" >> proxies.txt
fi

# Check phone numbers file exists
if [ ! -f "phones.txt" ]; then
    echo "[!] Creating phone numbers file..."
    echo "# Add phone numbers here" > phones.txt
    echo "+1234567890" >> phones.txt
    echo "+9876543210" >> phones.txt
    echo "941362292387221" >> phones.txt
fi

echo "[+] Starting main tool..."
python3 spam.py "$@"
