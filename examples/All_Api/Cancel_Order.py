import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers, default_root_uri, routes
from colorama import init, Fore
init(autoreset=True)

order_id = input("Enter the order_id to cancel: ").strip() or "3391250523777"  # Default or user input

route = routes['cancel_order'].format(order_id=order_id)
url = f"{default_root_uri}{route}"

response = requests.delete(url, headers=get_headers())
print(Fore.GREEN + "Order Cancel==>" + Fore.YELLOW + response.text)