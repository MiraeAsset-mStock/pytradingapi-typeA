import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from tradingapi_a.__config__ import get_headers, default_root_uri, routes
from colorama import init, Fore, Style
init(autoreset=True)

security_token = 11536
interval = "minute"
from_date = "2024-08-02"  # Only the date part
to_date = "2024-08-04"    # Only the date part
constant_time = "09%3A15%3A00"

from_time = f"{from_date}+{constant_time}"
to_time = f"{to_date}+09%3A20%3A00"  # You can also use a constant or prompt for this

print(f"Current security_token: {security_token}")
print(f"Current interval: {interval}")
print(f"Current from_date: {from_date}")
print(f"Current to_date: {to_date}")
print(f"Constant time: {constant_time}")
choice = input("Do you want to continue with these values? (y/n): ").strip().lower()

if choice == 'n':
    security_token = input("Enter security_token: ").strip() or security_token
    interval = input("Enter interval (e.g., minute, day): ").strip() or interval
    from_date = input("Enter from_date (YYYY-MM-DD): ").strip() or from_date
    to_date = input("Enter to_date (YYYY-MM-DD): ").strip() or to_date
    # If you want to allow changing the time, uncomment below:
    # constant_time = input("Enter constant time (HH%3AMM%3ASS): ").strip() or constant_time
    from_time = f"{from_date}+{constant_time}"
    to_time = f"{to_date}+09%3A20%3A00"

route = routes['historical_chart'].format(security_token=security_token, interval=interval)
url = f"{default_root_uri}{route}?from={from_time}&to={to_time}"

response = requests.get(url, headers=get_headers())
print(Fore.GREEN + "historical data:" + Fore.RED + response.text)