import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import json
from tradingapi_a import __config__
from tradingapi_a.mconnect import MConnect
from colorama import init, Fore, Style
init(autoreset=True)
mconnect_obj = MConnect()

user_id = "your_user_id",
password = "your_password"

try:
    login_response = mconnect_obj.login(user_id, password)
    otp = input(Fore.YELLOW+"Enter your OTP: ")
    gen_response = mconnect_obj.generate_session(__config__.API_KEY, otp, "W")
    parsed = json.loads(gen_response.text)
    with open("access_token.txt", "w") as f:
        f.write(parsed["data"]["access_token"])
except Exception as e:
    print(e)  # Only print the error message from the API

