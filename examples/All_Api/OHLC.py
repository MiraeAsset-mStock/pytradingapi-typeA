import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from tradingapi_a.__config__ import get_headers, default_root_uri, routes
from colorama import init, Fore, Style
init(autoreset=True)

params = [
    ('i', 'NSE:ACC'),
    ('i', 'BSE:ACC')
]
# If you are using Futures and Options, replace 'NSE' with 'NFO' and 'BSE' with 'BFO'.
# Replace 'ACC' with the required script name for your instrument.
# For equities, keep 'NSE' or 'BSE' as is and just change 'ACC' to your desired script name.
url = f"{default_root_uri}{routes['market_ohlc']}/"
response = requests.get(url, headers=get_headers(), params=params)
print(Fore.GREEN + "OHLC Results==>" + Fore.YELLOW + response.text)