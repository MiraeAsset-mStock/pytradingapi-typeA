API_KEY="mticker_url="wss://ws.mstock.trade""
default_root_uri= "https://api.mstock.trade/"
routes= {
        "login": "openapi/typea/connect/login",
        "generate_session": "openapi/typea/session/token",
        "place_order": "openapi/typea/orders/regular",
        "modify_order": "openapi/typea/orders/regular/{order_id}",
        "cancel_order": "openapi/typea/orders/regular/{order_id}",
        "cancel_all": "openapi/typea/orders/cancelall",
        "order_book": "openapi/typea/orders",
        "order_details": "openapi/typea/order/details",
        "net_position": "openapi/typea/portfolio/positions",
        "calculate_order_margin": "openapi/typea/margins/orders",
        "holdings": "openapi/typea/portfolio/holdings",
        "health_statistics": "openapi/typea/Health/GetHealthStatistics",
        "historical_chart": "openapi/typea/instruments/historical/{security_token}/{interval}",
        "market_ohlc": "openapi/typea/instruments/quote/ohlc",
        "market_ltp": "openapi/typea/instruments/quote/ltp",
        "instrument_scrip": "openapi/typea/instruments/scriptmaster",
        "fund_summary": "openapi/typea/user/fundsummary",
        "trade_history": "openapi/typea/trades",
        "position_conversion": "openapi/typea/portfolio/convertposition",
        "loser_gainer":"openapi/typea/losergainer",
        "create_basket":"openapi/typea/CreateBasket",
        "fetch_basket":"openapi/typea/FetchBasket",
        "rename_basket":"openapi/typea/RenameBasket",
        "delete_basket":"openapi/typea/DeleteBasket",
        "calculate_basket":"openapi/typea/CalculateBasket"
    }
mticker_url="wss://ws.mstock.trade"
