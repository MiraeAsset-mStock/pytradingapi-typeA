import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers, default_root_uri, routes
from colorama import init, Fore, Style
init(autoreset=True)

# Default values
order_id = "525013015583"
segment = "E"

print(f"Current Order ID: {order_id}")
print(f"Current Segment: {segment}")
choice = input("Do you want to continue with these values? (y/n): ").strip().lower()

if choice == 'n':
    order_id = input("Enter Order ID: ").strip() or order_id
    segment = input("Enter Segment (e.g., NSE, BSE): ").strip() or segment

details_packet = {"order_no": order_id, "segment": segment}
url = f"{default_root_uri}/{routes['order_details']}"
response = requests.get(url, headers=get_headers(), data=details_packet)

print(Fore.GREEN + "Order Details==>", Fore.YELLOW + response.text)