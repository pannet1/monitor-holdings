from constants import logging, CNFG
from typing import List, Dict
from kiteconnect import KiteTicker


def filter_ws_keys(incoming: List[Dict]) -> List[Dict]:
    keys = ["instrument_token", "last_price", "ohlc"]
    new_lst = []
    if incoming and isinstance(incoming, list) and any(incoming):
        for dct in incoming:
            new_dct = {}
            for key in keys:
                if dct.get(key, None):
                    new_dct[key] = dct[key]
            new_lst.append(new_dct)
    return new_lst


class Wsocket:
    def __init__(self, kite, tokens):
        self.ticks = []
        self.tokens = tokens
        if CNFG["broker"] == "bypass":
            self.kws = kite.kws
        else:
            self.kws = KiteTicker(kite.api_key, kite.access_token)
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_error = self.on_error
        self.kws.on_reconnect = self.on_reconnect
        self.kws.on_noreconnect = self.on_noreconnect

        # Infinite loop on the main thread. Nothing after this will run.
        # You have to use the pre-defined callbacks to manage subscriptions.
        self.kws.connect(threaded=True)

    def on_ticks(self, ws, ticks):
        if any(ticks):
            self.ticks = filter_ws_keys(ticks)

    def on_connect(self, ws, response):
        if response:
            print(f"on connect: {response}")
        # Subscribe to a list of instrument_tokens (Index first).
        # self.tokens = [v for k, v in nse_symbols.items() if k == "instrument_token"]
        if any(self.tokens):
            ws.subscribe(self.tokens)
        # Set RELIANCE to tick in `full` mode.
        ws.set_mode(ws.MODE_QUOTE, self.tokens)

    def on_close(self, ws, code, reason):
        # On connection close stop the main loop
        # Reconnection will not happen after executing `ws.stop()`
        ws.stop()

    def on_error(self, ws, code, reason):
        # Callback when connection closed with error.
        logging.info(
            "Connection error: {code} - {reason}".format(code=code, reason=reason)
        )

    def on_reconnect(self, ws, attempts_count):
        # Callback when reconnect is on progress
        logging.info("Reconnecting: {}".format(attempts_count))

    # Callback when all reconnect failed (exhausted max retries)

    def on_noreconnect(self, ws):
        logging.info("Reconnect failed.")
