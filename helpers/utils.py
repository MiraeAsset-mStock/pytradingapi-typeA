# coding: utf-8
import os
import json

# Mock responses path
responses_path = {
    "base": "../mock_responses/",
    "login": "login.json",
    "generate_session":"generate_session.json",
    "place_order":"place_order.json",
    "modify_order":"modify_order.json",
    "cancel_all":"cancel_all.json",
    "order_book":"get_order_book.json",
    "order_details":"order_details.json",
    "net_position":"get_net_positions.json",
    "calculate_order_margin":"calc_order_margin.json",
    "holdings":"holdings.json",
    "historical_chart":"historical_chart.json",
    "market_ohlc":"fetch_OHLC.json",
    "market_ltp":"fetch_LTP.json",
    "instrument_scrip":"instrument_scrip_master.csv",
    "fund_summary":"fund_summary.json",
    "trade_history":"trade_history.json",
    "position_conversion":"position_convert.json",

}


def full_path(rel_path):
    """return the full path of given rel_path."""
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            rel_path
        )
    )


def get_response(key):
    """Get mock response based on route."""
    path = full_path(responses_path["base"] + responses_path[key])
    return open(path, "r").read()


def get_json_response(key):
    """Get json mock response based on route."""
    return json.loads(get_response(key))