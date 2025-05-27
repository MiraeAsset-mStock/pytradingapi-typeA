import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers
from colorama import init, Fore, Style
init(autoreset=True)
from tradingapi_a.__config__ import default_root_uri
from tradingapi_a.__config__ import routes

data = {
    'fromdate': '2025-05-06', # <-- change as per your requirements
    'todate': '2025-05-20'    # <-- change as per your requirements
}
print(f"Current fromdate: {data['fromdate']}")
print(f"Current todate: {data['todate']}")
choice = input("Do you want to continue with these dates? (y/n): ").strip().lower()

if choice == 'n':
    fromdate = input("Enter fromdate (YYYY-MM-DD): ").strip() or data['fromdate']
    todate = input("Enter todate (YYYY-MM-DD): ").strip() or data['todate']
    data['fromdate'] = fromdate
    data['todate'] = todate
url = f"{default_root_uri}/{routes['trade_history']}"
response = requests.get(url,headers=get_headers(),data=data)
print(Fore.GREEN+"TradeHistory Results==>"+ Fore.YELLOW+ response.text)























# url = f"{default_root_uri}/{routes['trade_history']}"
# response = requests.get(url, headers=get_headers(),data=data)