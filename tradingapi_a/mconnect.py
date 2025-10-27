import os
import json
import logging
import requests
import sys,traceback
import tradingapi_a.exceptions as ex
from tradingapi_a import __config__
from urllib.parse import urljoin


#Creating Default Log file for API
default_log = logging.getLogger("mconnect.log")
default_log.addHandler(logging.FileHandler("mconnect.log", mode='a'))

class MConnect:
    
    _default_timeout = 7
    
    def __init__(self,api_key=None,access_Token=None,pool=None,timeout=None,debug=True,logger=default_log,disable_ssl=True): 
        self.api_key=api_key
        self.access_token=access_Token
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.timeout = timeout or self._default_timeout
        self.debug=debug
        self.logger=logger

        #Read config.json and assign
        
        self.default_root_uri=__config__.default_root_uri
        self.routes=__config__.routes

        # Create requests session by default
        # Same session to be used by pool connections
        self.request_session = requests.Session()
        if pool:
            request_adapter = requests.adapters.HTTPAdapter(**pool)
            self.request_session.mount("https://", request_adapter)

        # disable requests SSL warning
        requests.packages.urllib3.disable_warnings()

    def set_session_expiry_hook(self, method):
        """
        Set a callback hook for session (`TokenError` -- timeout, expiry etc.) errors.
        """
        if not callable(method):
            raise TypeError("Invalid input type. Only functions are accepted.")

        self.session_expiry_hook = method

    def login(self,user_id,password):
        '''
        Login with credentials 
        '''
        data={"Username":user_id,"Password":password}
        try:
            login_response=self._post(
                route="login",
                content_type="application/x-www-form-urlencoded",
                params=data
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e 
        return login_response
    
    def set_access_token(self, access_token):
        """Set the `access_token` received after a successful authentication."""
        self.access_token = access_token

    def set_api_key(self,api_key):
        """Set the API Key received after successful authentication and session generated"""
        self.api_key=api_key

    def generate_session(self,_api_key,_request_token,_checksum):
        '''
        Method to retrieve a session token based on api_key, request token and the checksum
        '''
        data={"api_key":_api_key,"request_token":_request_token,"checksum":_checksum}
        try:
            gen_session=self._post(
                route="generate_session",
                content_type="application/x-www-form-urlencoded",
                params=data
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        if "data" in gen_session.json():
            if "access_token" in gen_session.json()["data"]:
                self.set_access_token(gen_session.json()["data"]["access_token"])
        if self.api_key is None:
            self.set_api_key(_api_key)
        return gen_session
    
    def verify_totp(self,_api_key,_tOtp):
        '''
        Method for TOTP verification for valid clients
        '''
        data={"api_key":_api_key,"totp":_tOtp}
        try:
            verify_totp_user=self._post(
                route="verify_totp",
                content_type="application/x-www-form-urlencoded",
                params=data
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        if "data" in verify_totp_user.json():
            if "access_token" in verify_totp_user.json()["data"]:
                self.set_access_token(verify_totp_user.json()["data"]["access_token"])
        if self.api_key is None:
            self.set_api_key(_api_key)
        return verify_totp_user
    
    #Added variety parameter on 25-06-25 to allow regular,CO and AMO orders
    def place_order(self,_variety,_tradingsymbol,_exchange,_transaction_type,_order_type,_quantity,_product,_validity,_price,_trigger_price):
        '''
        Place a regular trading order in the provided segment
        '''
        #Added condition for AMO, regular or CO order
        api_route="place_order"
        if str(_variety).upper()=="CO":
            api_route="cover_order"
        elif str(_variety).upper()=="AMO":
            api_route="amo_order"
        elif str(_variety).upper()=="REGULAR":
            api_route="place_order"
        else:
            #incase of order types not available
            return {"status":"error","message":"Only order types NORMAL,AMO and COVER are available."}
        order_packet={"tradingsymbol":_tradingsymbol,"exchange":_exchange,"transaction_type":_transaction_type,"order_type":_order_type,"quantity":_quantity,"product":_product,"validity":_validity,"price":_price,"trigger_price":_trigger_price}
        try:
            order_session=self._post(
                route=api_route,
                content_type="application/x-www-form-urlencoded",
                params=order_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return order_session
    
    def modify_order(self,order_id,_order_type,_quantity,_price,_validity,_trigger_price,_disclosed_quantity):
        '''
        Update/Modify an existing order based on order_id provided
        '''
        url_args={"order_id": order_id}
        order_packet={"order_type":_order_type,"quantity":_quantity,"price":_price,"validity":_validity,"trigger_price":_trigger_price,"disclosed_quantity":_disclosed_quantity}
        try:
            modify_session=self._put(
                route="modify_order",
                url_args=url_args,
                params=order_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return modify_session
    
    def cancel_order(self,_orderID):
        '''
        Cancel an existing order based on user_id
        '''
        url_args={"order_id": _orderID}
        try:
            cancel_session=self._delete(
                route="cancel_order",
                url_args=url_args,
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return cancel_session
    
    def cancel_all(self):
        '''
        Method to cancel all the orders at once.
        '''
        try:
            #Changed to post on 29-07-25 by shri
            cancelAll_session=self._post(
                route="cancel_all",
                url_args=None,
            )

        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return cancelAll_session

    def get_order_book(self):
        '''
        Method to retrieve a list of all existing trading orders
        '''
        try:
            get_ord_book=self._get(
                route="order_book",
                url_args=None,
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_ord_book
    
    def get_order_details(self,_order_id,_segment="E"):
        '''
        Method to retrieve the status of individual order using the order id.
        '''
        details_packet={"order_no":_order_id,"segment":_segment}
        try:
            #Changed to post method on 29-07-25 by shri
            get_ord_details=self._post(
                route="order_details",
                url_args=None,
                content_type="application/x-www-form-urlencoded",
                params=details_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_ord_details

    def get_net_position(self):
        try:
            get_position=self._get(
                route="net_position",
                url_args=None,
                content_type=None
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_position
    
    def calculate_order_margin(self,_exchange,_tradingsymbol,_transaction_type,_variety,_product,_order_type,_quantity,_price,_trigger_price):
        params={"exchange":_exchange,"tradingsymbol":_tradingsymbol,"transaction_type":_transaction_type,"variety":_variety,"product":_product,"order_type":_order_type,"quantity":_quantity,"price":_price,"trigger_price":_trigger_price}
        try:
            ord_margin=self._post(
                route="calculate_order_margin",
                url_args=None,
                content_type="application/json",
                params=params,
                is_json=True
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return ord_margin
    
    #New Endpoint
    def get_holdings(self):
        '''
        Method to retrieve all the list of holdings that contain the user's portfolio of long term equity delivery stocks.
        '''
        url = urljoin(self.default_root_uri, self.routes["holdings"])
        try:
            get_holdings=self._get(
                route="holdings",
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_holdings
    
    #New Endpoint
    def get_historical_chart(self,_segment,_security_token,_interval,_fromDate,_toDate):
        url_args={"segment": _segment,"security_token": _security_token,"interval":_interval}

        date_range={"from":_fromDate,"to":_toDate}
        try:
            #Using session request
            #get_hist_chart=self.request_session.request("GET", url,headers=headers,params=date_range)
            get_hist_chart=self._get(
                route="historical_chart",
                url_args=url_args,
                content_type="application/x-www-form-urlencoded",
                params=date_range
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        ##Adding to debug logs if flag set to true
        #if self.debug:
        #    self.logger.debug("Request: {method} {url} {params} {headers}".format(method="GET", url=url,params=date_range, headers=headers))
        return get_hist_chart
    
    #New Endpoint
    def get_ohlc(self,ohlc_input):
        '''
        ohlc_input: List of strings in exchange:trading symbol format
        '''
        try:
            #Using session request
            get_ohlc_data=self._get(
                route="market_ohlc",
                url_args=None,
                params=[("i", symbol) for symbol in ohlc_input]
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_ohlc_data
    
    #New Endpoint
    def get_ltp(self,ltp_input):
        '''
        ltp_input: List of strings in exchange:trading symbol format
        '''
        try:
            #Using session request
            get_ltp_data=self._get(
                route="market_ltp",
                url_args=None,
                params=[("i", symbol) for symbol in ltp_input]
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_ltp_data
    
    def get_instruments(self):
        try:
            #Using session request
            get_instrument=self._get(
                route="instrument_scrip",
                url_args=None
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_instrument
    
    def get_fund_summary(self):
        try:
            #Using session request
            get_fund_summary=self._get(
                route="fund_summary",
                url_args=None
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_fund_summary
    

    def get_trade_history(self,_fromDate,_toDate):
        details_packet={"fromdate":_fromDate,"todate":_toDate}
        try:
            #Using session request - need to use POST to send form data
            get_trade=self._post(
                route="trade_history",
                url_args=None,
                content_type="application/x-www-form-urlencoded",
                params=details_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return get_trade

    def convert_position(self,_tradingsymbol,_exchange,_transaction_type,_position_type,_quantity,_old_product,_new_product):
        position_packet={"tradingsymbol":_tradingsymbol,"exchange":_exchange,"transaction_type":_transaction_type,"position_type":_position_type,"quantity":_quantity,"old_product":_old_product,"new_product":_new_product}
        try:
            conv_position=self._post(
                route="position_conversion",
                url_args=None,
                content_type="application/x-www-form-urlencoded",
                params=position_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return conv_position
    
    def loser_gainer(self,_Exchange,_SecurityIdCode,_segment,_typeFlag):
        data_packet={"Exchange":_Exchange,"SecurityIdCode":_SecurityIdCode,"segment":_segment,"TypeFlag":_segment,"TypeFlag":_typeFlag}
        try:
            _loserGainer=self._post(
                route="loser_gainer",
                url_args=None,
                content_type="application/x-www-form-urlencoded",
                params=data_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return _loserGainer
    
    def create_basket(self,_BaskName,_BaskDesc):
        bask_packet={"BaskName":_BaskName,"BaskDesc":_BaskDesc}
        try:
            createBasket=self._post(
                    route="create_basket",
                    url_args=None,
                    content_type="application/x-www-form-urlencoded",
                    params=bask_packet
                )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return createBasket
        
    def fetch_basket(self):
        try:
            basket=self._get(
                route="fetch_basket",
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return basket
    
    def rename_basket(self,_basketName,_BasketId):
        try:
            data_packet={"basketName":_basketName,"BasketId":_BasketId}
            _rename_basket=self._put(
                route="rename_basket",
                url_args=None,
                content_type="application/x-www-form-urlencoded",
                params=data_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return _rename_basket

    def delete_basket(self,_BasketId):
        try:
            data_packet={"BasketId":_BasketId}
            _delete_basket=self._delete(
                route="delete_basket",
                url_args=None,
                content_type="application/x-www-form-urlencoded",
                params=data_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return _delete_basket

    def calculate_basket(self,_include_exist_pos,_ord_product,_disc_qty,_segment,_trigger_price,_scriptcode,_ord_type,_basket_name,_operation,_order_validity,_order_qty,_script_stat,_buy_sell_indi,_basket_priority,_order_price,_basket_id,_exch_id):
        try:
            data_packet={"include_exist_pos":_include_exist_pos,"ord_product":_ord_product,"disc_qty":_disc_qty,"segment":_segment,"trigger_price":_trigger_price,"scriptcode":_scriptcode,"ord_type":_ord_type,"basket_name":_basket_name,"operation":_operation,"order_validity":_order_validity,"order_qty":_order_qty,"script_stat":_script_stat,"buy_sell_indi":_buy_sell_indi,"basket_priority":_basket_priority,"order_price":_order_price,"basket_id":_basket_id,"exch_id":_exch_id}
            _calculate_basket=self._post(
                route="calculate_basket",
                url_args=None,
                content_type="application/x-www-form-urlencoded",
                params=data_packet
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return _calculate_basket

    def get_trade_book(self):
        try:
            trade_book_details=self._get(
                route="trade_book",
                url_args=None,
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
        return trade_book_details

    def get_intraday_chart(self,_segment_id,_symbol):
        try:
            url_args={"segment_id": _segment_id,"symbol":_symbol}
            intday_chart=self._get(
                route="intraday_chart",
                url_args=url_args,
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace) 
        return intday_chart

    def get_option_chain_master(self,_exchangeID):
        try:
            url_args={"exchange_id":_exchangeID}
            opt_chain_mast=self._get(
                route="option_chain_master",
                url_args=url_args
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
        return opt_chain_mast

    def get_option_chain_data(self,_exchange_id,_expiry,_token):
        try:
            url_args={"exchange_id":_exchange_id,"expiry":_expiry,"token":_token}
            opt_chain_data=self._get(
                route="option_chain_data",
                url_args=url_args
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
        return opt_chain_data

    def logout(self):
        try:
            logout=self._get(
                route="logout",
                url_args=None
            )
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            stack_trace = traceback.format_exception(type_, value_, traceback_)
            self.logger.error(stack_trace)
            raise e
        return logout

    #Aliases for get,post,delete requests
    def _get(self, route, url_args=None, content_type=None, params=None, is_json=False):
        """Alias for sending a GET request."""
        return self._request(route, "GET", url_args=url_args,content_type=content_type, params=params, is_json=is_json)

    def _post(self, route, url_args=None, content_type=None, params=None, is_json=False, query_params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", url_args=url_args,content_type=content_type, params=params, is_json=is_json, query_params=query_params)

    def _put(self, route, url_args=None, content_type=None, params=None, is_json=False, query_params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", url_args=url_args,content_type=content_type, params=params, is_json=is_json, query_params=query_params)

    def _delete(self, route, url_args=None, content_type=None, params=None, is_json=False):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", url_args=url_args,content_type=content_type, params=params, is_json=is_json)
    
    def _request(self, route, method, url_args=None, content_type=None,params=None, is_json=False, query_params=None):
        """Make an HTTP request."""
        # Form a restful URL
        if url_args:
            uri = self.routes[route].format(**url_args)
        else:
            uri = self.routes[route]

        url = urljoin(self.default_root_uri, uri)

        # Custom headers
        headers = {
            "X-Mirae-Version": "1"
        }

        if content_type:
            headers["Content-Type"]=str(content_type)
            
        if self.api_key and self.access_token:
            # set authorization header
            auth_header = self.api_key + ":" + self.access_token
            headers["Authorization"] = "token {}".format(auth_header)

        #Adding to debug logs if flag set to true
        if self.debug:
            if is_json:
                self.logger.debug("Request: {method} {url} {json} {headers}".format(method=method, url=url, json=params, headers=headers))
            else:
                self.logger.debug("Request: {method} {url} {data} {headers}".format(method=method, url=url, data=params, headers=headers))
        
        # prepare url query params
        if method in ["GET"]: #, "DELETE"
            if isinstance(params, list) and all(isinstance(p, tuple) and len(p) == 2 for p in params):
                # Handle list of tuples for multiple parameters with same key
                query_params = params
            else:
                query_params = params

        try:
            response_data = self.request_session.request(method,
                                        url,
                                        json=params if (method in ["POST", "PUT"] and is_json) else None,
                                        data=params if (method in ["POST", "PUT","DELETE"] and not is_json) else None,
                                        params=query_params if query_params else None,
                                        headers=headers,
                                        verify=not self.disable_ssl,
                                        allow_redirects=True,
                                        timeout=self.timeout)
        except Exception as e:
            raise e

        if self.debug:
            self.logger.debug("Response: {code} {content}".format(code=response_data.status_code, content=response_data.content))

        # Validate the content type.
        if "content-type" in response_data.headers:
            if "json" in response_data.headers["content-type"]:
                try:
                    data = response_data.json()
                except ValueError:
                    raise ex.DataException("Couldn't parse the JSON response received from the server: {content}".format(
                        content=response_data.content))

                if type(data)==list:
                    data=data[0]
                # api error
                if data.get("status") == "error":
                    if "error_type" in data:
                        # Call session hook if its registered and TokenException is raised
                        if self.session_expiry_hook and response_data.status_code == 403 and data["error_type"] == "TokenException":
                            self.session_expiry_hook()

                        # native Kite errors
                        exp = getattr(ex, data.get("error_type"), ex.GeneralException)
                        raise exp(data["message"], code=response_data.status_code)
                    else:
                        raise ex.GeneralException(data["message"], code=response_data.status_code)
            
            elif "csv" in response_data.headers["content-type"]:
                return response_data.content
            elif "text/plain" in response_data.headers["content-type"]:
                return response_data.text
            else:
                raise ex.DataException("Unknown Content-Type ({content_type}) with response: ({content})".format(
                    content_type=response_data.headers["content-type"],
                    content=response_data.content))

        return response_data

