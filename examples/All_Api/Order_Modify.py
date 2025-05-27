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
    "order_type": "LIMIT",
    "quantity": "2",
    "price": "7",
    "validity": "DAY",
    "disclosed_quantity": "0",
    "trigger_price": "684"
}

order_id = "3251250523250"  # Default order ID

print(f"Current order_id: {order_id}")
print("Current order data:")
for k, v in data.items():
    print(f"{k}: {v}")

choice = input("Do you want to continue with these values? (y/n): ").strip().lower()

if choice == 'n':
    new_order_id = input(f"Enter order_id (press Enter to keep '{order_id}'): ").strip()
    if new_order_id:
        order_id = new_order_id
    for k in data:
        new_val = input(f"Enter value for {k} (press Enter to keep '{data[k]}'): ").strip()
        if new_val:
            data[k] = new_val

route = routes['modify_order'].format(order_id=order_id)
url = f"{default_root_uri}{route}"
response = requests.put(url, headers=get_headers(), data=data)
print(Fore.GREEN + "Order Modify==>" + Fore.YELLOW + response.text)