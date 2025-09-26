import os,sys
import csv
import logging
 
 
parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)  # Insert at beginning to override installed package

from tradingapi_a.mticker import *
from tradingapi_a.mconnect import *
from tradingapi_a import __config__

# Create and configure logger
logging.basicConfig(filename="miraesdk_typeA_socket.log",
                    format='%(asctime)s %(message)s',
                    filemode='a',)

# Creating an object
test_logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
test_logger.setLevel(logging.INFO)

#Testing NConnect API
#Object for NConnect API
mconnect_obj=MConnect()

username="XXXXXXXX" #Replace with your username
password="XXXXXXXX" #Replace with your password

#Login Via Tasc API, Receive Token in response
login_response=mconnect_obj.login(username,password)
test_logger.info(f"Request : Login. Response received : {login_response.json()}")

## !!!! NOTE - Use generate_session() only when TOTP is NOT enabled for the user. Else use verify_totp() to generate access_token !!!!

# Generate session with OTP - access token by calling generate session
OTP=input("Enter OTP received on your registered mobile number : ")
gen_response=mconnect_obj.generate_session(__config__.API_KEY,OTP,"W")
test_logger.info(f"Request : Generate Session. Response received : {gen_response.json()}")

## !!!! NOTE - If TOTP is enabled for the user, then only call Verify TOTP. Else skip verify_totp() !!!!

# #Generate session with TOTP - Check Verify TOTP
# TOTP=input("Enter TOTP from Auhtenticator app : ")
# totp_verify=mconnect_obj.verify_totp(__config__.API_KEY,TOTP)
# print(f"Request : Verify TOTP. Response received : {totp_verify.json()}")

#Getting API Key
api_key=__config__.API_KEY

#Getting Access token
access_token=mconnect_obj.access_token

#Testing Web Socket or NTicker

m_ticker=MTicker(api_key,access_token,__config__.mticker_url)


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    test_logger.info("Ticks: {}".format(ticks))

def on_order_update(ws,data):
    #Callback to receive Order Updates
    test_logger.info("On Order Updates Packet received : {}".format(data))

def on_trade_update(ws,data):
    #Callback to receive Trade Updates
    test_logger.info("On Trade Updates Packet received : {}".format(data))

def on_connect(ws, response):
    # Callback on successful connect.
    m_ticker.send_login_after_connect()
    # Subscribe to a list of instrument_tokens .
    ws.subscribe([3456])
    # Set tick in LTP mode immediately after subscribe.
    ws.set_mode(m_ticker.MODE_QUOTE, [3456])

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
m_ticker.on_ticks = on_ticks
m_ticker.on_connect = on_connect
m_ticker.on_close = on_close
#Assigning Order Update Callback
m_ticker.on_order_update=on_order_update
#Assigning Trade Update Callback
m_ticker.on_trade_update=on_trade_update

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
m_ticker.connect()

test_logger.info('Now Closing Web socket connection')

m_ticker.close()

test_logger.info('Testing complete')








