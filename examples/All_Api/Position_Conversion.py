import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers, default_root_uri, routes
from colorama import init, Fore
init(autoreset=True)

data = {
    "tradingsymbol": "RELIANCE25MAR1300CE",
    "exchange": "NFO",
    "transaction_type": "BUY",
    "position_type": "DAY",
    "quantity": "1",
    "old_product": "NRML",
    "new_product": "MIS"
}

print("Current position conversion data:")
for k, v in data.items():
    print(f"{k}: {v}")
choice = input("Do you want to continue with these values? (y/n): ").strip().lower()

if choice == 'n':
    for k in data:
        new_val = input(f"Enter value for {k} (press Enter to keep '{data[k]}'): ").strip()
        if new_val:
            data[k] = new_val

url = f"{default_root_uri}{routes['position_conversion']}"
response = requests.post(url, headers=get_headers(), data=data)
print(Fore.GREEN + "Position Conversion==>" + Fore.YELLOW + response.text)