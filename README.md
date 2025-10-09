## TradingAPI SDK - Python Client for accessing TradingAPI and Streaming Market Data

### Description
TradingAPI is a complete SDK that allows you to build a trading and investment platform which includes executing orders in real time, streaming live trade and order data (Using Websockets) and more. 

### Installation


> [!IMPORTANT]
> You can install the python client with below command. For requirements.txt file [refer here](https://github.com/MiraeAsset-mStock/pytradingapi-typeA/blob/main/requirements.txt).

```
pip install -r requirements.txt

pip install --upgrade mStock-TradingApi-A
```

It is recommended to update 'pip' and `setuptools` to the latest version if you are facing any issues during installation

```
pip install -U pip setuptools
```

>[!NOTE]
>The package can be used with the name **tradingapi_a**

### API Usage

```python
import logging
from tradingapi_a.mconnect import *

logging.basicConfig(level=logging.DEBUG)

#Object for MConnect API
mconnect_obj=MConnect()

#Login
login_response=mconnect_obj.login("<user_id>","<password>")

#Generate access token by calling generate session
gen_response=mconnect_obj.generate_session("<API_Key>","<request_token_here>","<checksum>")

#Verify TOTP (if enabled)
mconnect_obj.verify_totp("<API_Key>","<TOTP>")

#Place Order
porder_resp=mconnect_obj.place_order("regular","SBICARD","NSE","BUY","MARKET","10","CNC","DAY","0","0")
test_logger.info(f"Request : Place Order. Response received : {porder_resp.json()}")

#Modify Order
mconnect_obj.modify_order("order_id","SL","5","723","DAY","720","0")

#Cancel Order
mconnect_obj.cancel_order("order_id")

#Cancel All orders
mconnect_obj.cancel_all()

#Get Order Details
mconnect_obj.get_order_details("order_id")

#Fetch all orders
mconnect_obj.get_order_book()

#Get Net position for logged in user
mconnect_obj.get_net_position()

#Calculate Order Margin
mconnect_obj.calculate_order_margin("NSE","INFY","BUY","regular","CNC","MARKET","1","0","0")

#Fetch all holdings
mconnect_obj.get_holdings()

#Get Historical Chart
mconnect_obj.get_historical_chart("NSE","11536","60minute","2025-01-05","2025-01-10")

#Get Trade History
mconnect_obj.get_trade_history("2025-01-05","2025-01-10")

#Get OHLC Data
mconnect_obj.get_ohlc(["NSE:ACC","BSE:ACC"])

#Get LTP Data
mconnect_obj.get_ltp(["NSE:ACC","BSE:ACC"])

#Get Instrument Master
mconnect_obj.get_instruments()

#Get fund Summary
mconnect_obj.get_fund_summary()

#Convert Position
mconnect_obj.convert_position("TCS","NSE","BUY","DAY","3","CNC","MIS")

#Loser Gainer
mconnect_obj.loser_gainer("1","13","1","G")

#Create Basket
mconnect_obj.create_basket("Test Basket","Test Basket Description")

#Fetch Basket
mconnect_obj.fetch_basket()

#Rename Basket
mconnect_obj.rename_basket("New Basket Name","basket_id")

#Delete Basket
mconnect_obj.delete_basket("basket_id")

#Calculate Basket
mconnect_obj.calculate_basket("0","C","0","E","0","11915","LMT","Test Basket","I","DAY","1","A","B","1","19.02","269","NSE")

#Get Trade Book
mconnect_obj.get_trade_book()

#Get Intraday Chart
mconnect_obj.get_intraday_chart("4","AUBANK")

#Get Option Chain Master
mconnect_obj.get_option_chain_master("5")

#Get Option Chain Data
mconnect_obj.get_option_chain_data("2","1432996200","22")

#Logout
mconnect_obj.logout()

```

### Websocket Usage
```python
from tradingapi_a.mticker import *
import logging

logging.basicConfig(level=logging.DEBUG)

#Testing Web Socket or MTicker
m_ticker=MTicker("<API_KEY>","<ACCESS_TOKEN>","<WEB_SOCKET_URL>")


#Defining Callbacks
def on_ticks(ws, ticks):
    # Callback to receive ticks.
    logging.info("Ticks: {}".format(ticks))

def on_order_update(ws,data):
    #Callback to receive Order Updates
    logging.info("On Order Updates Packet received : {}".format(data))

def on_trade_update(ws,data):
    #Callback to receive Trade Updates
    logging.info("On Trade Updates Packet received : {}".format(data))

def on_connect(ws, response):
    # Callback on successful connect.
    m_ticker.send_login_after_connect()
    # Subscribe to a list of instrument_tokens .
    ws.subscribe([5633])
    # Set tick in `full` mode.
    ws.set_mode(m_ticker.MODE_FULL, [5633])

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
m_ticker.on_ticks = on_ticks
m_ticker.on_connect = on_connect
m_ticker.on_close = on_close
m_ticker.on_order_update=on_order_update
m_ticker.on_trade_update=on_trade_update

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
m_ticker.connect()

logging.info('Now Closing Web socket connection')

m_ticker.close()

logging.info('Testing complete')


```

### Running Unit Tests

This requires having pytest library pre installed. You can install the same via pip:

``` pip install pytest ```

Navigate to the ```unit``` directory and run the ```connect_test.py``` file using pytest

```
cd unit
pytest connect_test.py
```

### Support
For issues, please open an issue on GitHub.

### Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a new branch (feature-xyz)
3. Commit your changes
4. Push the branch and create a pull request
