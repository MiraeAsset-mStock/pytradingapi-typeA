import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers
from colorama import init, Fore
init(autoreset=True)
from tradingapi_a.__config__ import default_root_uri
from tradingapi_a.__config__ import routes

data = {
    "tradingsymbol": "BANKNIFTY25JUL32000CE",
    "exchange": "NFO",
    "transaction_type": "BUY",
    "order_type": "SL-M",
    "quantity": "35",
    "product": "MIS",
    "validity": "DAY",
    "price": "0",
    "trigger_price": "74"
}

print("Current SL-M order data:")
for k, v in data.items():
    print(f"{k}: {v}")
choice = input("Do you want to continue with these values? (y/n): ").strip().lower()

if choice == 'n':
    for k in data:
        new_val = input(f"Enter value for {k} (press Enter to keep '{data[k]}'): ").strip()
        if new_val:
            data[k] = new_val

url = f"{default_root_uri}{routes['place_order']}"
response = requests.post(url, headers=get_headers(), data=data)
print(Fore.GREEN + " FO Order Placement==>" + Fore.YELLOW + response.text)