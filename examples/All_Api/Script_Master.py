import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers
from colorama import init, Fore
init(autoreset=True)
from tradingapi_a.__config__ import default_root_uri
from tradingapi_a.__config__ import routes

url = f"{default_root_uri}/{routes['instrument_scrip']}"
response = requests.get(url, headers=get_headers())
print(Fore.GREEN+"Script Master==>"+Fore.YELLOW+ response.text)