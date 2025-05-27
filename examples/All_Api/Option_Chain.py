import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import requests
from tradingapi_a.__config__ import get_headers
from colorama import init, Fore, Style
init(autoreset=True)
from tradingapi_a.__config__ import default_root_uri
from tradingapi_a.__config__ import routes

exch = "2"            # Exchange code, e.g., "2"
expiry = "1432996200" # Expiry code/token (as per your requirement)
token = "22"          # Token (as per your requirement)

print(f"Current values:\nExchange: {exch}\nExpiry: {expiry}\nToken: {token}")
choice = input("Do you want to use the existing values? (y/n): ").strip().lower()

if choice == 'n':
    exch = input("Enter Exchange code (e.g., 2): ").strip() or exch
    expiry = input("Enter Expiry code/token: ").strip() or expiry
    token = input("Enter Token: ").strip() or token
url = f"{default_root_uri}{routes['option_chain']}".format(
    exch=exch, expiry=expiry, token=token
)
response = requests.get(url, headers=get_headers())
print(Fore.GREEN + "Option_Chain==>"+ Fore.YELLOW+ response.text)
