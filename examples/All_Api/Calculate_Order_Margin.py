import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers, default_root_uri, routes
from colorama import init, Fore
init(autoreset=True)

data = {
    "exchange": "NFO",
    "tradingsymbol": "ACC25FEB1800CE",
    "transaction_type": "BUY",
    "variety": "regular",
    "product": "CNC",
    "order_type": "MARKET",
    "quantity": 10,
    "price": 1500,
    "trigger_price": 0
}

print("Current margin calculation data:")
for k, v in data.items():
    print(f"{k}: {v}")
choice = input("Do you want to continue with these values? (y/n): ").strip().lower()

if choice == 'n':
    for k in data:
        new_val = input(f"Enter value for {k} (press Enter to keep '{data[k]}'): ").strip()
        if new_val:
            # Convert numeric fields to int/float if needed
            if k in ["quantity", "price", "trigger_price"]:
                try:
                    data[k] = float(new_val) if '.' in new_val else int(new_val)
                except ValueError:
                    data[k] = new_val
            else:
                data[k] = new_val

url = f"{default_root_uri}{routes['calculate_order_margin']}"
headers = get_headers()
headers["Content-Type"] = "application/json"
response = requests.post(url, headers=headers, data=json.dumps(data))
print(Fore.GREEN + "Calculate Order Margin==>" + Fore.YELLOW + response.text)