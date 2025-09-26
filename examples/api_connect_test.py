import os,sys
import csv
import logging

parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from tradingapi_a.mconnect import *
from tradingapi_a import __config__

# Create and configure logger
logging.basicConfig(filename="miraesdk_typeA.log",
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

# #Generate session with OTP - access token by calling generate session
OTP=input("Enter OTP received on your registered mobile number : ")
gen_response=mconnect_obj.generate_session(__config__.API_KEY,OTP,"W")
test_logger.info(f"Request : Generate Session. Response received : {gen_response.json()}")

## !!!! NOTE - If TOTP is enabled for the user, then only call Verify TOTP. Else skip verify_totp() !!!!

#Generate session with TOTP - Check Verify TOTP
# TOTP=input("Enter TOTP from Auhtenticator app : ")
# totp_verify=mconnect_obj.verify_totp(__config__.API_KEY,TOTP)
# print(f"Request : Verify TOTP. Response received : {totp_verify.json()}")

#Getting API Key
api_key=__config__.API_KEY

#Getting Access token
access_token=mconnect_obj.access_token

#Test Order Placement, Modification etc

#Place Order
porder_resp=mconnect_obj.place_order("regular","SBICARD","NSE","BUY","MARKET","10","CNC","DAY","0","0")
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
order_det=mconnect_obj.get_order_details("1151250205102")
test_logger.info(f"Request : Order Details. Response received : {order_det.json()}")

#Get Holdings
holdings=mconnect_obj.get_holdings()
test_logger.info(f"Request : Holdings. Response received : {holdings.json()}")


#Get Historical Chart
historical_chart=mconnect_obj.get_historical_chart("NSE","11536","60minute","2025-01-05","2025-01-10") 
test_logger.info(f"Request : Historical Chart. Response received : {historical_chart.json()}")

#Trade History
trade_history=mconnect_obj.get_trade_history("2025-01-05","2025-01-10")
test_logger.info(f"Request : Trade History. Response received : {trade_history.json()}")

#OHLC
get_ohlc=mconnect_obj.get_ohlc(["NSE:ACC","BSE:ACC","NSE:RVNL","BSE:TATAMOTORS","NSE:TATAMOTORS"])
print("ohlc",get_ohlc.json())
test_logger.info(f"Request : Fetch Market Data OHLC. Response received : {get_ohlc.json()}")

#LTP
get_ltp=mconnect_obj.get_ltp(["NSE:ACC","BSE:ACC","NSE:RVNL","BSE:TATAMOTORS"])
print("ltp",get_ltp.json())
test_logger.info(f"Request : Fetch Market Data LTP. Response received : {get_ltp.json()}")

#Get Instrument Scrip Master
get_instruments=mconnect_obj.get_instruments()
split_data=get_instruments.decode('utf-8').split("\n")
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

#Loser Gainer
los_gain=mconnect_obj.loser_gainer("1","13","1","G")
test_logger.info(f"Request : Loser Gainer. Response received : {los_gain.json()}")

#Create Basket
cre_basket=mconnect_obj.create_basket("Tets Baskett","Tets Bakset Description")
test_logger.info(f"Request : Create Basket. Response received : {cre_basket.json()}")

#Fetch Basket
fetch_bask=mconnect_obj.fetch_basket()
test_logger.info(f"Request : Fetch Basket. Response received : {fetch_bask.json()}")

#Rename Basket
rename_bask=mconnect_obj.rename_basket("Test_New","251")
test_logger.info(f"Request : Rename Basket. Response received : {rename_bask.json()}")

#Delete Basket
del_basket=mconnect_obj.delete_basket("251")
test_logger.info(f"Request : Delete Basket. Response received : {del_basket.json()}")

#Calculate Basket
calc_basket=mconnect_obj.calculate_basket("0","C","0","E","0","11915","LMT","Test Basket Updated Renamed","I","DAY","1","A","B","1","19.02","269","NSE")
test_logger.info(f"Request : Calculate Basket. Response received : {calc_basket.json()}")

#Get Trade Book
trade_book=mconnect_obj.get_trade_book()
test_logger.info(f"Request : Get Trade Book. Response received : {trade_book.json()}")

#Get Intraday chart
intr_chart=mconnect_obj.get_intraday_chart("4","AUBANK")
test_logger.info(f"Request : Get Intraday chart data. Response received : {intr_chart.json()}")

#Get Option Chain Master
opt_chain_master=mconnect_obj.get_option_chain_master("5")
test_logger.info(f"Request : Get Option Chain Master. Response received : {opt_chain_master.json()}")

#Get Option Chain data
opt_chain_data=mconnect_obj.get_option_chain_data("2","1432996200","22")
test_logger.info(f"Request : Get Option Chain Data. Response received : {opt_chain_data.json()}")

#Logout
logout=mconnect_obj.logout()
test_logger.info(f"Request : Logout : {logout.json()}")















