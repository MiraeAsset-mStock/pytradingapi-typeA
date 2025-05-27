import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import default_root_uri, routes, get_headers
from colorama import init, Fore, Style
init(autoreset=True)

url = f"{default_root_uri}/{routes['fund_summary']}"
response = requests.get(url, headers=get_headers())
print(Fore.GREEN+"Fund Summary==>"+Fore.YELLOW+ response.text)