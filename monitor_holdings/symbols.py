from constants import O_FUTL, S_DATA, logging
import pandas as pd
from traceback import print_exc
from typing import Dict, List, Any


# what exchange and its symbols should be dumped
exchanges = ["NSE", "BSE"]


def get_symbols(exchange: str) -> Dict[str, Dict[str, Any]]:
    try:
        json = {}
        url = f"https://api.kite.trade/instruments/{exchange}"
        df = pd.read_csv(url)
        # keep only tradingsymbol and instrument_token
        df = df[
            [
                "tradingsymbol",
                "instrument_token",
            ]
        ]
        json = df.to_dict(orient="records")
        # flatten list in dictionary values
    except Exception as e:
        logging.error(f"{str(e)} while getting symbols from {exchange}")
        print_exc()
    finally:
        return json


def dump():
    try:
        # iterate each exchange
        for exchange in exchanges:
            exchange_file = S_DATA + exchange + ".json"
            if O_FUTL.is_file_not_2day(exchange_file):
                sym_from_json = get_symbols(exchange)
                O_FUTL.write_file(exchange_file, sym_from_json)
    except Exception as e:
        print(f"dump error: {e}")
        print_exc()


def get_tokens_from_list(exch_syms: List) -> Dict:
    try:
        # split exch_sym into tradingsymbol and instrument_token
        new_dct = {}
        for exch_sym in exch_syms:
            exch, tradingsymbol = exch_sym.split(":")[0], exch_sym.split(":")[1]
            lst = O_FUTL.read_file(S_DATA + exch + ".json")
            for dct in lst:
                if dct["tradingsymbol"] == tradingsymbol:
                    new_dct[exch_sym] = dct["instrument_token"]
        return new_dct
    except Exception as e:
        print(f"get_tokens_from_symbols error: {e}")
        print_exc()


if __name__ == "__main__":
    dct = get_tokens_from_list(["NSE:INFY", "BSE:SBIN"])
    print(dct)
