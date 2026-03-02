'''
This is the socket based implementation: nFeed_OpenAPI
'''
import time
import sys
import six
import json
import threading
import struct
import logging
from datetime import datetime,timezone,timedelta
from twisted.internet import reactor,ssl
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from twisted.python import log as twisted_log

default_log = logging.getLogger("mticker.log")
default_log.addHandler(logging.FileHandler("mticker.log", mode='a'))

class MTickerClientProtocol(WebSocketClientProtocol):
    PING_INTERVAL = 2.5
    KEEPALIVE_INTERVAL = 5

    _next_ping = None
    _next_pong_check = None
    _last_pong_time = None
    _last_ping_time = None
    
    def __init__(self, *args, **kwargs):
        """Initialize protocol with all options passed from factory."""
        super(MTickerClientProtocol, self).__init__(*args, **kwargs)

    def onConnect(self, response):  # noqa
        """Called when WebSocket server connection was established"""
        self.factory.ws = self

        if self.factory.on_connect:
            self.factory.on_connect(self, response)

        # Reset reconnect on successful reconnect
        self.factory.resetDelay()

    def onOpen(self):  # noqa
        """Called when the initial WebSocket opening handshake was completed."""
        # send ping
        self._loop_ping()
        # init last pong check after X seconds
        self._loop_pong_check()

        if self.factory.on_open:
            self.factory.on_open(self)

    def onMessage(self, payload, is_binary):  # noqa
        """Called when text or binary message is received."""
        if self.factory.on_message:
            self.factory.on_message(self, payload, is_binary)

    def onClose(self, was_clean, code, reason):  # noqa
        """Called when connection is closed."""
        if not was_clean:
            if self.factory.on_error:
                self.factory.on_error(self, code, reason)

        if self.factory.on_close:
            self.factory.on_close(self, code, reason)

        # Cancel next ping and timer
        self._last_ping_time = None
        self._last_pong_time = None

        if self._next_ping:
            self._next_ping.cancel()

        if self._next_pong_check:
            self._next_pong_check.cancel()

    def onPong(self, response):  # noqa
        """Called when pong message is received."""
        if self._last_pong_time and self.factory.debug:
            default_log("last pong was {} seconds back.".format(time.time() - self._last_pong_time))

        self._last_pong_time = time.time()

        if self.factory.debug:
            default_log("pong => {}".format(response))

    """
    Custom helper and exposed methods.
    """

    def _loop_ping(self):  # noqa
        """Start a ping loop where it sends ping message every X seconds."""
        if self.factory.debug:
            if self._last_ping_time:
                default_log.debug("last ping was {} seconds back.".format(time.time() - self._last_ping_time))

        # Set current time as last ping time
        self._last_ping_time = time.time()

        # Call self after X seconds
        self._next_ping = self.factory.reactor.callLater(self.PING_INTERVAL, self._loop_ping)

    def _loop_pong_check(self):
        """
        Timer sort of to check if connection is still there.

        Checks last pong message time and disconnects the existing connection to make sure it doesn't become a ghost connection.
        """
        if self._last_pong_time:
            # No pong message since long time, so init reconnect
            last_pong_diff = time.time() - self._last_pong_time
            if last_pong_diff > (2 * self.PING_INTERVAL):
                if self.factory.debug:
                    default_log.debug("Last pong was {} seconds ago. So dropping connection to reconnect.".format(
                        last_pong_diff))
                # drop existing connection to avoid ghost connection
                self.dropConnection(abort=True)

        # Call self after X seconds
        self._next_pong_check = self.factory.reactor.callLater(self.PING_INTERVAL, self._loop_pong_check)


class MTickerClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    """Autobahn WebSocket client factory to implement reconnection and custom callbacks."""
    protocol = MTickerClientProtocol
    maxDelay = 5
    maxRetries = 10

    _last_connection_time = None

    def __init__(self, *args, **kwargs):
        """Initialize with default callback method values."""
        self.debug = False
        self.ws = None
        self.on_open = None
        self.on_error = None
        self.on_close = None
        self.on_message = None
        self.on_connect = None
        self.on_reconnect = None
        self.on_noreconnect = None

        super(MTickerClientFactory, self).__init__(*args, **kwargs)

    def startedConnecting(self, connector):  # noqa
        """On connecting start or reconnection."""
        if not self._last_connection_time and self.debug:
            default_log.debug("Start WebSocket connection.")

        self._last_connection_time = time.time()

    def clientConnectionFailed(self, connector, reason):  # noqa
        """On connection failure (When connect request fails)"""
        if self.retries > 0:
            default_log.error("Retrying connection. Retry attempt count: {}. Next retry in around: {} seconds".format(self.retries, int(round(self.delay))))

            # on reconnect callback
            if self.on_reconnect:
                self.on_reconnect(self.retries)

        # Retry the connection
        self.retry(connector)
        self.send_noreconnect()

    def clientConnectionLost(self, connector, reason):  # noqa
        """On connection lost (When ongoing connection got disconnected)."""
        if self.retries > 0:
            # on reconnect callback
            if self.on_reconnect:
                self.on_reconnect(self.retries)

        # Retry the connection
        self.retry(connector)
        self.send_noreconnect()

    def send_noreconnect(self):
        """Callback `no_reconnect` if max retries are exhausted."""
        if self.maxRetries is not None and (self.retries > self.maxRetries):
            if self.debug:
                default_log.debug("Maximum retries ({}) exhausted.".format(self.maxRetries))
                # Stop the loop for exceeding max retry attempts
                self.stop()
                
            if self.on_noreconnect:
                self.on_noreconnect()


class MTicker(object):
    EXCHANGE_MAP = {
        "nse": 1,
        "nfo": 2,
        "cds": 3,
        "bse": 4,
        "bfo": 5,
        "bcd": 6,
        "mcx": 7,
        "mcxsx": 8,
        "indices": 9,
        "bsecds": 6,
    }

    # Default connection timeout
    CONNECT_TIMEOUT = 30
    # Default Reconnect max delay.
    RECONNECT_MAX_DELAY = 60
    # Default reconnect attempts
    RECONNECT_MAX_TRIES = 50
    # Default root API endpoint. It's possible to
    # override this by passing the `root` parameter during initialisation.

    # Available streaming modes.
    MODE_FULL = "full"
    MODE_QUOTE = "quote"
    MODE_LTP = "ltp"

    # Flag to set if its first connect
    _is_first_connect = True

    # Available actions.
    _message_code = 11
    _message_subscribe = "subscribe"
    _message_unsubscribe = "unsubscribe"
    _message_setmode = "mode"

    # Minimum delay which should be set between retries. User can't set less than this
    _minimum_reconnect_max_delay = 5
    # Maximum number or retries user can set
    _maximum_reconnect_max_tries = 300

    def __init__(self, api_key,access_token, root,debug=False, 
                 reconnect=True, reconnect_max_tries=RECONNECT_MAX_TRIES, reconnect_max_delay=RECONNECT_MAX_DELAY,
                 connect_timeout=CONNECT_TIMEOUT): #aDDED API_KEY PARAMETER

        self.root = root #or self.ROOT_URI

        # Set max reconnect tries
        if reconnect_max_tries > self._maximum_reconnect_max_tries:
            default_log.warning("`reconnect_max_tries` can not be more than {val}. Setting to highest possible value - {val}.".format(
                val=self._maximum_reconnect_max_tries))
            self.reconnect_max_tries = self._maximum_reconnect_max_tries
        else:
            self.reconnect_max_tries = reconnect_max_tries

        # Set max reconnect delay
        if reconnect_max_delay < self._minimum_reconnect_max_delay:
            default_log.warning("`reconnect_max_delay` can not be less than {val}. Setting to lowest possible value - {val}.".format(
                val=self._minimum_reconnect_max_delay))
            self.reconnect_max_delay = self._minimum_reconnect_max_delay
        else:
            self.reconnect_max_delay = reconnect_max_delay

        self.connect_timeout = connect_timeout

        #Adding access token variable
        self.access_token=access_token

        
        self.api_key=api_key
        
        #Changed format on 06-02-25
        self.socket_url = "{root}?ACCESS_TOKEN={access_token}&API_KEY={api_key}".format(
                root=self.root,
                access_token=access_token,
                api_key=api_key
            )
        # Debug enables logs
        self.debug = debug

        # Initialize default value for websocket object
        self.ws = None

        # Placeholders for callbacks.
        self.on_ticks = None
        self.on_open = None
        self.on_close = None
        self.on_error = None
        self.on_connect = None
        self.on_message = None
        self.on_reconnect = None
        self.on_noreconnect = None

        # Text message updates
        #For Orders
        self.on_order_update = None
        #For Trades
        self.on_trade_update=None


        # List of current subscribed tokens
        self.subscribed_tokens = {}

    def _create_connection(self, url, **kwargs):
        """Create a WebSocket client connection."""
        self.factory = MTickerClientFactory(url, **kwargs)

        # Alias for current websocket connection
        self.ws = self.factory.ws
        self.factory.debug = self.debug

        # Register private callbacks
        self.factory.on_open = self._on_open
        self.factory.on_error = self._on_error
        self.factory.on_close = self._on_close
        self.factory.on_message = self._on_message
        self.factory.on_connect = self._on_connect
        self.factory.on_reconnect = self._on_reconnect
        self.factory.on_noreconnect = self._on_noreconnect

        self.factory.maxDelay = self.reconnect_max_delay
        self.factory.maxRetries = self.reconnect_max_tries

    def connect(self, threaded=False, disable_ssl_verification=False, proxy=None):

        # Init WebSocket client factory
        self._create_connection(self.socket_url,
                                proxy=proxy) 

        # Set SSL context
        context_factory = None
        if self.factory.isSecure and not disable_ssl_verification:
            context_factory = ssl.ClientContextFactory()

        # Establish WebSocket connection to a server
        connectWS(self.factory, contextFactory=context_factory, timeout=self.connect_timeout)

        if self.debug:
            twisted_log.startLogging(sys.stdout)

        # Run in seperate thread of blocking
        opts = {}

        # Run when reactor is not running
        if not reactor.running:
            if threaded:
                # Signals are not allowed in non main thread by twisted so suppress it.
                opts["installSignalHandlers"] = False
                self.websocket_thread = threading.Thread(target=reactor.run, kwargs=opts)
                self.websocket_thread.daemon = True
                self.websocket_thread.start()
            else:
                reactor.run(**opts)

    def is_connected(self):
        """Check if WebSocket connection is established."""
        if self.ws and self.ws.state == self.ws.STATE_OPEN: 
            return True
        else:
            return False

    def _close(self, code=None, reason=None):
        """Close the WebSocket connection."""
        if self.ws:
            self.ws.sendClose(code, reason)

    def close(self, code=None, reason=None):
        """Close the WebSocket connection."""
        self.stop_retry()
        self._close(code, reason)

    def stop(self):
        """Stop the event loop. Should be used if main thread has to be closed in `on_close` method.
        Reconnection mechanism cannot happen past this method
        """
        if reactor.running:
            reactor.stop()

    def stop_retry(self):
        """Stop auto retry when it is in progress."""
        if self.factory:
            self.factory.stopTrying()

    def send_login_after_connect(self):
        try:
            #Send Login:AccessToken to socket to maintain connection
            self.ws.sendMessage(six.b(f"LOGIN:{self.access_token}"))
            return True
        except Exception as e:
            self._close(reason="Error while subscribe: {}".format(str(e)))
            raise

    def subscribe(self, instrument_tokens):
        """
        Subscribe to a list of instrument_tokens.

        - `instrument_tokens` is list of instrument instrument_tokens to subscribe
        """
        try:
            self.ws.sendMessage(
                six.b(json.dumps({"a": self._message_subscribe, "v": instrument_tokens}))
            )

            for token in instrument_tokens:
                self.subscribed_tokens[token] = self.MODE_QUOTE
 
            return True
        except Exception as e:
            self._close(reason="Error while subscribe: {}".format(str(e)))
            raise

    def unsubscribe(self, instrument_tokens):
        """
        Unsubscribe the given list of instrument_tokens.

        - `instrument_tokens` is list of instrument_tokens to unsubscribe.
        """
        try:
            self.ws.sendMessage(
                six.b(json.dumps({"a": self._message_unsubscribe, "v": instrument_tokens}))
            )
            for token in instrument_tokens:
                try:
                    del (self.subscribed_tokens[token])
                except KeyError:
                    pass

            return True
        except Exception as e:
            self._close(reason="Error while unsubscribe: {}".format(str(e)))
            raise


    def set_mode(self, mode, instrument_tokens):
        """
        Set streaming mode for the given list of tokens.

        - `mode` is the mode to set. It can be one of the following class constants:
            MODE_LTP, MODE_QUOTE, or MODE_FULL.
        - `instrument_tokens` is list of instrument tokens on which the mode should be applied
        """
        try:
            self.ws.sendMessage(
                six.b(json.dumps({"a": self._message_setmode, "v": [mode, instrument_tokens]}))
            )

            # Update modes
            for token in instrument_tokens:
                self.subscribed_tokens[token] = mode

            return True
        except Exception as e:
            self._close(reason="Error while setting mode: {}".format(str(e)))
            raise

    def resubscribe(self):
        """Resubscribe to all current subscribed tokens."""
        modes = {}

        for token in self.subscribed_tokens:
            m = self.subscribed_tokens[token]

            if not modes.get(m):
                modes[m] = []

            modes[m].append(token)

        for mode in modes:
            if self.debug:
                default_log.debug("Resubscribe and set mode: {} - {}".format(mode, modes[mode]))

            self.subscribe(modes[mode])
            self.set_mode(mode, modes[mode])


    def _on_connect(self, ws, response):
        self.ws = ws
        if self.on_connect:
            print("WebSocket connected")
            self.on_connect(self, response)

    def _on_close(self, ws, code, reason):
        """Call `on_close` callback when connection is closed."""
        default_log.error("Connection closed: {} - {}".format(code, str(reason)))

        if self.on_close:
            self.on_close(self, code, reason)

    def _on_error(self, ws, code, reason):
        """Call `on_error` callback when connection throws an error."""
        default_log.error("Connection error: {} - {}".format(code, str(reason)))

        if self.on_error:
            self.on_error(self, code, reason)

    def _on_message(self, ws, payload, is_binary):
        """Call `on_message` callback when text message is received."""
        if self.on_message:
            self.on_message(self, payload, is_binary)

        # If the message is binary, parse it and send it to the callback.
        if self.on_ticks and is_binary and len(payload) > 4:
            self.on_ticks(self, self._parse_binary(payload))
        elif is_binary:
            default_log.info(f"Received binary message with length {len(payload)} (too short to parse)")

        # Parse text messages
        if not is_binary:
            self._parse_text_message(payload)

    def _on_open(self, ws):
        # Resubscribe if its reconnect
        if not self._is_first_connect:
            self.resubscribe()

        # Set first connect to false once its connected first time
        self._is_first_connect = False
        
        if self.on_open:
            return self.on_open(self)

    def _on_reconnect(self, attempts_count):
        if self.on_reconnect:
            return self.on_reconnect(self, attempts_count)

    def _on_noreconnect(self):
        if self.on_noreconnect:
            return self.on_noreconnect(self)
    
    def _parse_text_message(self, payload):
        """Parse text message."""
        # Decode unicode data
        if not six.PY2 and type(payload) == bytes:
            payload = payload.decode("utf-8")
        
        try:
            data = json.loads(payload)
        except ValueError:
            return

        
        # Order update callback
        if self.on_order_update and data.get("type") == "order" and data.get("data"):
            self.on_order_update(self, data["data"])

        #Trade Update Callback
        if self.on_trade_update and data.get("type") == "trade" and data.get("data"):
            self.on_trade_update(self, data["data"])

        # Custom error with websocket error code 0
        if data.get("type") == "error":
            self._on_error(self, 0, data.get("data"))

    def convert_from_unix_timestamp(self,timeStamp: int, year=1980):
        # Convert Unix timestamp into a datetime value
        origin = datetime(year, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        if timeStamp != 0:
            return origin + timedelta(seconds=timeStamp)
        return origin
    
    def _parse_binary(self, bin):
        """Parse binary data to a (list of) ticks structure."""
        try:
            packets = self._split_packets(bin)  # split data to individual ticks packet
        except Exception as e:
            default_log.error(f"Error splitting packets: {e}")
            return []
        
        data = []

        for packet in packets:
            try:
                instrument_token = self._unpack_int(packet, 0, 4)
                segment = instrument_token & 0xff  # Retrive segment constant from instrument_token

                # Add price divisor based on segment
                #Right now keeping it 100 for all
                divisor = 100.0

                # All indices are not tradable
                tradable = False if segment == self.EXCHANGE_MAP["indices"] else True

                # LTP packets
                if len(packet) == 8:
                    data.append({
                        "tradable": tradable,
                        "mode": self.MODE_LTP,
                        "instrument_token": instrument_token,
                        "last_price": self._unpack_int(packet, 4, 8) / divisor
                    })
                    # Indices quote and full mode
                elif len(packet) == 28 or len(packet) == 32:
                    mode = self.MODE_QUOTE if len(packet) == 28 else self.MODE_FULL

                    d = {
                        "tradable": tradable,
                        "mode": mode,
                        "instrument_token": instrument_token,
                        "last_price": self._unpack_int(packet, 4, 8) / divisor,
                        "ohlc": {
                                "high": self._unpack_int(packet, 8, 12) / divisor,
                                "low": self._unpack_int(packet, 12, 16) / divisor,
                                "open": self._unpack_int(packet, 16, 20) / divisor,
                                "close": self._unpack_int(packet, 20, 24) / divisor
                            }
                        }

                    # Compute the change price using close price and last price
                    d["change"] = 0
                    if (d["ohlc"]["close"] != 0):
                        d["change"] = (d["last_price"] - d["ohlc"]["close"]) * 100 / d["ohlc"]["close"]

                    # Full mode with timestamp
                    if len(packet) == 32:
                        try:
                            #Changing to custom method on 01-07-25
                            # timestamp = datetime.fromtimestamp(self._unpack_int(packet, 28, 32)).strftime("%Y-%m-%dT%I:%M:%S%p")
                            timestamp = self.convert_from_unix_timestamp(self._unpack_int(packet, 28, 32)).strftime("%Y-%m-%dT%I:%M:%S%p")
                        except Exception as e:
                            print(e)
                            timestamp = None

                        d["exchange_timestamp"] = timestamp
                    data.append(d)
                # Index full mode with 52-week high/low
                elif len(packet) == 48:
                    requested_mode = self.subscribed_tokens.get(instrument_token, self.MODE_FULL)
                    d = {
                        "tradable": tradable,
                        "mode": requested_mode,
                        "instrument_token": instrument_token,
                        "last_price": self._unpack_int(packet, 4, 8) / divisor,
                        "ohlc": {
                            "open": self._unpack_int(packet, 8, 12) / divisor,
                            "high": self._unpack_int(packet, 12, 16) / divisor,
                            "low": self._unpack_int(packet, 16, 20) / divisor,
                            "close": self._unpack_int(packet, 20, 24) / divisor
                        }
                    }
                    d["change"] = 0
                    if d["ohlc"]["close"] != 0:
                        d["change"] = (d["last_price"] - d["ohlc"]["close"]) * 100 / d["ohlc"]["close"]
                    try:
                        d["last_traded_timestamp"] = self.convert_from_unix_timestamp(self._unpack_int(packet, 24, 28)).strftime("%Y-%m-%dT%I:%M:%S%p")
                    except:
                        d["last_traded_timestamp"] = None
                    d["open_interest"] = 0
                    d["open_interest_high"] = 0
                    d["open_interest_low"] = 0
                    try:
                        d["exchange_timestamp"] = self.convert_from_unix_timestamp(self._unpack_int(packet, 28, 32)).strftime("%Y-%m-%dT%I:%M:%S%p")
                    except:
                        d["exchange_timestamp"] = None
                    d["upper_circuit"] = self._unpack_int(packet, 32, 36) / divisor
                    d["lower_circuit"] = self._unpack_int(packet, 36, 40) / divisor
                    d["52_Week_High"] = self._unpack_int(packet, 40, 44) / divisor
                    d["52_Week_Low"] = self._unpack_int(packet, 44, 48) / divisor
                    data.append(d)
                # Quote mode for non indices
                elif len(packet) == 44:
                    mode = self.MODE_QUOTE
                # Full mode for non indices  
                elif len(packet) == 184 or len(packet) == 200:
                    mode = self.MODE_FULL
                
                if len(packet) == 44 or len(packet) == 184 or len(packet) == 200:
                    # Check requested mode for this token
                    requested_mode = self.subscribed_tokens.get(instrument_token, mode)
                    
                    d = {
                        "tradable": tradable,
                        "mode": requested_mode,
                        "instrument_token": instrument_token,
                        "last_price": self._unpack_int(packet, 4, 8) / divisor
                    }
                    
                    if requested_mode == self.MODE_LTP:
                        # LTP mode - add all fields but set most to 0/null
                        d.update({
                            "last_traded_quantity": 0,
                            "average_traded_price": 0.0,
                            "volume_traded": 0,
                            "total_buy_quantity": 0,
                            "total_sell_quantity": 0,
                            "ohlc": {"open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0},
                            "change": 0.0,
                            "depth": None,
                            "last_traded_timestamp": None,
                            "open_interest": 0,
                            "open_interest_high": 0,
                            "open_interest_low": 0,
                            "exchange_timestamp": None
                        })
                    else:
                        d.update({
                            "last_traded_quantity": self._unpack_int(packet, 8, 12),
                            "average_traded_price": self._unpack_int(packet, 12, 16) / divisor,
                            "volume_traded": self._unpack_int(packet, 16, 20),
                            "total_buy_quantity": self._unpack_int(packet, 20, 24),
                            "total_sell_quantity": self._unpack_int(packet, 24, 28),
                            "ohlc": {
                                "open": self._unpack_int(packet, 28, 32) / divisor,
                                "high": self._unpack_int(packet, 32, 36) / divisor,
                                "low": self._unpack_int(packet, 36, 40) / divisor,
                                "close": self._unpack_int(packet, 40, 44) / divisor
                            }
                        })

                        #Adding more as per documentation for non-LTP modes
                        if requested_mode != self.MODE_LTP:
                            try:
                                d["last_traded_timestamp"]=self.convert_from_unix_timestamp(self._unpack_int(packet, 44, 48)).strftime("%Y-%m-%dT%I:%M:%S%p")
                            except Exception as e:
                                d["last_traded_timestamp"] = None

                            d["open_interest"]=self._unpack_int(packet,48,52)/divisor,
                            d["open_interest_high"]=self._unpack_int(packet,52,56)/divisor,
                            d["open_interest_low"]=self._unpack_int(packet,56,60)/divisor,
                            try:
                                d["exchange_timestamp"] = self.convert_from_unix_timestamp(self._unpack_int(packet, 60, 64)).strftime("%Y-%m-%dT%I:%M:%S%p")
                            except Exception as e:
                                d["exchange_timestamp"] = None

                            # Compute the change price using close price and last price
                            d["change"] = 0
                            if (d["ohlc"]["close"] != 0):
                                d["change"] = (d["last_price"] - d["ohlc"]["close"]) * 100 / d["ohlc"]["close"]

                            # Parse full mode depth data
                            if (len(packet) == 184 or len(packet) == 200) and requested_mode == self.MODE_FULL:
                                depth = {
                                        "bid": [],
                                        "ask": []
                                    }
                                
                                # For 200-byte packets, depth data starts at byte 64, same as 184-byte packets
                                depth_start = 64
                                depth_end = min(len(packet), 184)  # Limit to 184 to match expected format
                                
                                for i,p in enumerate(range(depth_start, depth_end, 12)):
                                    if p + 12 <= len(packet):
                                        depth["ask" if i >= 5 else "bid"].append({
                                            "quantity": self._unpack_int(packet, p, p + 4) if len(packet[p: p + 4]) == 4 else 0,
                                            "price": self._unpack_int(packet, p + 4, p + 8) / divisor if len(packet[p+4: p + 8]) == 4 else 0,
                                            "orders": self._unpack_int(packet, p + 8, p + 10, byte_format="H") if len(packet[p + 8: p + 10]) == 2 else 0,
                                            "padding": self._unpack_int(packet, p + 10, p + 12, byte_format="H") if len(packet[p + 10: p + 12]) == 2 else 0,
                                        })

                                d["depth"] = depth
                                
                                # Parse additional fields for 200-byte packets
                                if len(packet) == 200:
                                    d["upper_circuit"] = self._unpack_int(packet, 184, 188) / divisor
                                    d["lower_circuit"] = self._unpack_int(packet, 188, 192) / divisor
                                    d["52_Week_High"] = self._unpack_int(packet, 192, 196) / divisor
                                    d["52_Week_Low"] = self._unpack_int(packet, 196, 200) / divisor

                    data.append(d)
            except Exception as e:
                default_log.error(f"Error parsing packet: {e}, packet length: {len(packet)}, token: {instrument_token if 'instrument_token' in locals() else 'unknown'}")
                continue
        
        default_log.info(f"Returning {len(data)} ticks")
        return data

    def _unpack_int(self, bin, start, end, byte_format="I"):
        """Unpack binary data as unsigned interger."""
        data_slice = bin[start:end]
        expected_size = 4 if byte_format == "I" else 2 if byte_format == "H" else 1
        
        if len(data_slice) != expected_size:
            default_log.error(f"Buffer size mismatch: expected {expected_size}, got {len(data_slice)}")
            return 0
            
        return struct.unpack(">" + byte_format, data_slice)[0]

    def _split_packets(self, bin):
        """Split the data to individual packets of ticks."""
        # Ignore heartbeat data.
        if len(bin) < 2:
            return []

        number_of_packets = self._unpack_int(bin, 0, 2, byte_format="H")
        packets = []

        j = 2
        for i in range(number_of_packets):
            packet_length = self._unpack_int(bin, j, j + 2, byte_format="H")
            packets.append(bin[j + 2: j + 2 + packet_length])
            j = j + 2 + packet_length

        return packets

