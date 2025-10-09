import os,sys
import pytest
import responses
from urllib.parse import urljoin

parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from helpers import utils
import tradingapi_a.exceptions as ex

@responses.activate
def test_place_order(mconnect):
    '''Test Place Order'''
    responses.add(
        responses.POST,
        urljoin(mconnect.default_root_uri, mconnect.routes["place_order"]),
        body=utils.get_response("place_order"),
        content_type="application/json"
    )
    new_order=mconnect.place_order("SBICARD","NSE","BUY","MARKET","10","CNC","DAY","0","0" )
    assert new_order


@responses.activate
def test_get_order_book(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["order_book"]),
        body=utils.get_response('order_book'),
        content_type="application/json"
    )
    get_ord_bk=mconnect.get_order_book()
    assert type(get_ord_bk.json())==dict
    assert type(get_ord_bk.json()["data"])==list

@responses.activate
def test_positions(mconnect):
    """Test positions."""
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["net_position"]),
        body=utils.get_response("net_position"),
        content_type="application/json"
    )
    positions = mconnect.get_net_position()
    assert type(positions.json()) == dict
    assert "data" in positions.json()
    assert "net" in positions.json()["data"]

@responses.activate
def test_holdings(mconnect):
    """Test holdings."""
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["holdings"]),
        body=utils.get_response("holdings"),
        content_type="application/json"
    )
    holdings = mconnect.get_holdings()
    assert type(holdings.json()) == dict

@responses.activate
def test_historical_chart(mconnect):
    """Test Historical Chart"""
    url_args={"security_token": "11536","interval":"60minute"}
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["historical_chart"].format(**url_args)),
        body=utils.get_response("historical_chart"),
        content_type="application/json"
    )
    hist_chart=mconnect.get_historical_chart("11536","60minute","2025-01-05","2025-01-10")
    assert type(hist_chart.json())==dict
    assert "candles" in hist_chart.json()["data"]

@responses.activate
def test_trade_history(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["trade_history"]),
        body=utils.get_response("trade_history"),
        content_type="application/json"
    )
    trade_hist=mconnect.get_trade_history("2025-01-05","2025-01-10")
    assert type(trade_hist.json())==dict

@responses.activate
def test_fetch_ohlc(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["market_ohlc"]),
        body=utils.get_response("market_ohlc"),
        content_type="application/json"
    )
    fetch_ohlc=mconnect.get_ohlc(["NSE:ACC","BSE:ACC"])
    assert fetch_ohlc.json()

@responses.activate
def test_fetch_ltp(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["market_ltp"]),
        body=utils.get_response("market_ltp"),
        content_type="application/json"
    )
    fetch_ltp=mconnect.get_ltp(["NSE:ACC","BSE:ACC"])
    assert fetch_ltp.json()

@responses.activate
def test_instrument_scrip(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["instrument_scrip"]),
        body=utils.get_response("instrument_scrip"),
    )
    get_instruments=mconnect.get_instruments()
    split_data=get_instruments.split("\n")
    data=[row.strip().split(",") for row in split_data]
    assert data

@responses.activate
def test_fund_summary(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["fund_summary"]),
        body=utils.get_response("fund_summary"),
        content_type="application/json"
    )

    fund_summ=mconnect.get_fund_summary()
    assert fund_summ
    #assert type(fund_summ.json())==dict
    #assert "data" in fund_summ.json()

@responses.activate
def test_order_details(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["order_details"]),
        body=utils.get_response("order_details"),
        content_type="application/json"
    )
    order_dets=mconnect.get_order_details("1151250205102","E")
    assert type(order_dets.json())==dict
    assert "data" in order_dets.json() 


@responses.activate
def test_calc_order_margin(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["calculate_order_margin"]),
        body=utils.get_response("calculate_order_margin"),
        content_type="application/json"
    )
    calc_order_margin=mconnect.calculate_order_margin("NSE","INFY","BUY","regular","CNC","MARKET","1","0","0")
    assert type(calc_order_margin.json())==dict
    assert "data" in calc_order_margin.json()
    assert type(calc_order_margin.json()["data"])==dict

@responses.activate
def test_cancel_all(mconnect):
    responses.add(
        responses.GET,
        urljoin(mconnect.default_root_uri, mconnect.routes["cancel_all"]),
        body=utils.get_response("cancel_all"),
        content_type="application/json"
    )
    cancel_all_orders=mconnect.cancel_all()
    assert type(cancel_all_orders.json())==dict

@responses.activate
def test_conv_position(mconnect):
    responses.add(
        responses.POST,
        urljoin(mconnect.default_root_uri, mconnect.routes["position_conversion"]),
        body=utils.get_response("position_conversion"),
        content_type="application/json"
    )
    conv_position=mconnect.convert_position("TCS","NSE","BUY","DAY","3","CNC","MIS")
    assert type(conv_position.json())==dict
    assert "data" in conv_position.json()

@responses.activate
def test_modify_order(mconnect):
    '''Test Modify Order'''
    url_args={"order_id": "1181250203103"}
    responses.add(
        responses.PUT,
        urljoin(mconnect.default_root_uri, mconnect.routes["modify_order"].format(**url_args)),
        body=utils.get_response("modify_order"),
        content_type="application/json"
    )
    mod_order=mconnect.modify_order("1181250203103","SL","5","723","DAY","720","0")
    assert mod_order

