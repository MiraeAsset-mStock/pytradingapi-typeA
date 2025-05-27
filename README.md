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

#Place Order
try:
    porder_resp=mconnect_obj.place_order(_tradingsymbol="SBICARD",_exchange="NSE",_transaction_type="BUY",_order_type="MARKET",_quantity="10",_product="CNC",_validity="DAY",_price="0",_trigger_price="0")
    
    logging.info("Order placed. ID is: {}".format(porder_resp["data"]["order_id"]))

except Exception as e:
    logging.info("Order placement failed: {}".format(e.message))

#Fetch all orders
mconnect_obj.get_order_book()

#Fetch all holdings
mconnect_obj.get_holdings()

#Get Net position for logged in user
mconnect_obj.get_net_position()

#Cancel All orders
mconnect_obj.cancel_all()

#Get fund Summary
mconnect_obj.get_fund_summary()

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
### Example API Scripts

The `examples/All_Api` folder contains ready-to-use scripts for various API operations, such as:

- `Calculate_Order_Margin.py` – Calculate margin required for an order
- `Cancel_Order.py` – Cancel a specific order
- `Cancel_All_Orders.py` – Cancel all open orders
- `FundsSummary.py` – Get fund summary
- `Holdings.py` – Fetch holdings
- `Instrument_historical.py` – Fetch historical data for an instrument
- `Intraday_Chart.py` – Get intraday chart data
- `Limit_Order_Placement.py` – Place a limit order
- `Login.py` – Login and session management
- `Market_LTP.py` – Get last traded price (LTP)
- `OHLC.py` – Get OHLC data
- `Option_Chain_Master.py` – Get option chain master
- `Option_Chain.py` – Get option chain data
- `Order_Book.py` – Fetch order book
- `Order_Details_individual.py` – Get details of a specific order
- `Order_Modify.py` – Modify an existing order
- `Order_Placement.py` – Place a regular order
- `Position_Conversion.py` – Convert position type
- `Position.py` – Get current positions
- `Script_Master.py` – Get script master data
- `SL_Order_Placement.py` – Place a stop loss order
- `SL-M_Order_Placement.py` – Place a stop loss market order
- `Trade_book.py` – Fetch trade book
- `Trades_History.py` – Get trade history

**How to Run:**

- **Using the Run icon:**  
  Open any `.py` file in your editor (like VS Code) and click the **Run** icon at the top right.

- **Using the command line:**  
  ```bash
  python path_of_the_python_file_that_you_want_to_run


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
