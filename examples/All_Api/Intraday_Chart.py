import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers, default_root_uri, routes
from colorama import init, Fore
init(autoreset=True)

# Default values
exchange = "1"         # e.g., "1" for NSE, "BSE" for BSE, etc.
scriptName = "AUBANK"  # e.g., "AUBANK"
interval = "minute"    # e.g., "minute", "day"

print(f"Current exchange: {exchange}")
print(f"Current scriptName: {scriptName}")
print(f"Current interval: {interval}")
choice = input("Do you want to continue with these values? (y/n): ").strip().lower()

if choice == 'n':
    exchange = input("Enter exchange (e.g., 1 for NSE): ").strip() or exchange
    scriptName = input("Enter script name (e.g., AUBANK): ").strip() or scriptName
    interval = input("Enter interval (e.g., minute, day): ").strip() or interval

route = routes['intraday_chart'].format(exchange=exchange, scriptName=scriptName, interval=interval)
url = f"{default_root_uri}{route}"

response = requests.get(url, headers=get_headers())
print(Fore.GREEN + "Script Master==>" + Fore.YELLOW + response.text)