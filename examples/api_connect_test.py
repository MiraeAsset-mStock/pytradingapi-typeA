 pip intall git+https://github.com/MiraeAsset-mStock/pytradingapi-typeA.git

import os,sys
import csv
import logging
import json

from tradingapi_a.mconnect import *
from tradingapi_a import __config__
print('asfasf')
# Create and configure logger
logging.basicConfig(filename="miraesdk_typeA.log",
                    format='%(asctime)s %(message)s',
                    filemode='a',)

# Creating an object
test_logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
test_logger.setLevel(logging.INFO)

__config__.API_KEY="QxEvDCS4vqB37/avSE++uQ@@"
api_key=__config__.API_KEY

#Testing NConnect API
#Object for NConnect API
mconnect_obj=MConnect()
print("ok")
def first_login():
    login_response=mconnect_obj.login("user_id","password")
    print('sending 3 digit token...')
    token=input('please enter token you received on mobile or email:')
    gen_response=mconnect_obj.generate_session(__config__.API_KEY,token,"W")
    data={'access_token':(gen_response.json()['data']['access_token'])}      
    with open("access_token.json", "w") as json_file:
        json.dump(data, json_file, indent=4)    
def second_login():
    with open("access_token.json", "r") as file:
        data = json.load(file)
        # Get the value of 'access_token'
        access_token = data["access_token"]

    mconnect_obj.set_api_key(api_key)
    mconnect_obj.set_access_token(access_token)

try:
    second_login()
except Exception as e:
    try:
        first_login()
    except Exception as e:
        print("error:",e)    
  
#Test Order Placement, Modification etc

#Place Order
porder_resp=mconnect_obj.place_order("SBICARD","NSE","BUY","MARKET","10","CNC","DAY","0","0")
test_logger.info(f"Request : Place Order. Response received : {porder_resp.json()}")

#Modify Order
modify_resp=mconnect_obj.modify_order("1181250203103","SL","5","723","DAY","720","0")
test_logger.info(f"Request : Modify Order. Response received : {modify_resp.json()}")

#Cancel Order by Order ID
cancel_resp=mconnect_obj.cancel_order("1181250205102")
test_logger.info(f"Request : Cancel Order. Response received : {cancel_resp}")

#Get Order book for logged in user
get_ord_bk=mconnect_obj.get_order_book()
test_logger.info(f"Request : Get Order Book. Response received : {get_ord_bk.json()}")

#Get Net position for logged in user
get_net_pos=mconnect_obj.get_net_position()
test_logger.info(f"Request : Get Net Positions. Response received : {get_net_pos.json()}")

#Calculate order MArgin given the details
calc_ord_margin=mconnect_obj.calculate_order_margin("NSE","INFY","BUY","regular","CNC","MARKET","1","0","0")
test_logger.info(f"Request : Calculate Order Margin. Response received : {calc_ord_margin.json()}")

#CANCEl All orders
cancel_all=mconnect_obj.cancel_all()
test_logger.info(f"Request : Cancel All. Response received : {cancel_all.json()}")

#Order Details
order_det=mconnect_obj.get_order_details("1151250205102","E")
test_logger.info(f"Request : Order Details. Response received : {order_det.json()}")

#Get Holdings
holdings=mconnect_obj.get_holdings()
test_logger.info(f"Request : Holdings. Response received : {holdings.json()}")

#Get Historical Chart
historical_chart=mconnect_obj.get_historical_chart("11536","60minute","2025-01-05","2025-01-10") 
test_logger.info(f"Request : Historical Chart. Response received : {historical_chart.json()}")

#Trade History
trade_history=mconnect_obj.get_trade_history("2025-01-05","2025-01-10")
test_logger.info(f"Request : Trade History. Response received : {trade_history.json()}")

#OHLC
get_ohlc=mconnect_obj.get_ohlc(["NSE:ACC","BSE:ACC"])
test_logger.info(f"Request : Fetch Market Data OHLC. Response received : {get_ohlc.json()}")

#LTP
get_ltp=mconnect_obj.get_ltp(["NSE:ACC","BSE:ACC"])
test_logger.info(f"Request : Fetch Market Data LTP. Response received : {get_ltp.json()}")

#Get Instrument Scrip Master
get_instruments=mconnect_obj.get_instruments()
split_data=get_instruments.text.split("\n")
data=[row.strip().split(",") for row in split_data]
#Writing response into a csv file for reference
#Open the file in write mode
with open('instrument_scrip_master.csv', mode='w') as file:
    # Create a csv.writer object
    writer = csv.writer(file,delimiter=",")
    # Write data to the CSV file
    for row in data:
        writer.writerow(row)

test_logger.info(f"Request : Fetch Instrument Scrip Master. Response received and stored in a csv file.")


#Get fund Summary
get_fund_summary=mconnect_obj.get_fund_summary()
test_logger.info(f"Request : Fetch Fund Summary. Response received : {get_fund_summary.json()}")

# #Convert Position
conv_position=mconnect_obj.convert_position("TCS","NSE","BUY","DAY","3","CNC","MIS")
test_logger.info(f"Request : Position Conversion. Response received : {conv_position.json()}")














