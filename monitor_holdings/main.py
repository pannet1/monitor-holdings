from toolkit.currency import round_to_paise
from login_get_kite import get_kite, remove_token
import sys
from time import sleep
from traceback import print_exc
from constants import logging, S_DATA, buff, secs, perc_col_name
from holdings import get
from symbols import dump, get_tokens_from_list
from wsocket import Wsocket
from typing import List, Dict
import pandas as pd


broker = get_kite()


def get_holdings():
    try:
        logging.debug("getting holdings for the day ...")
        resp = broker.kite.holdings()
        df = get(resp)
        logging.debug("filtering for required columns")
        df["key"] = df["exchange"] + ":" + df["tradingsymbol"]
        df.set_index("key", inplace=True)
        # df = df[df[perc_col_name] != False]
        df.drop(
            [
                "exchange",
                "tradingsymbol",
                "average_price",
                "last_price",
                "unrealized",
                "cap",
                perc_col_name,
            ],
            axis=1,
            inplace=True,
        )
    except Exception as e:
        print_exc()
        logging.error(f"{str(e)} while reading holdings")
        sys.exit(1)
    else:
        return df


def place_order(index, row):
    try:
        exchsym = index.split(":")
        logging.info(f"placing order for {index}, str{row}")
        order_id = broker.order_place(
            tradingsymbol=exchsym[1],
            exchange=exchsym[0],
            transaction_type="SELL",
            quantity=int(row["calculated"]),
            order_type="LIMIT",
            product="CNC",
            variety="regular",
            price=round_to_paise(row["ltp"], buff),
        )
        if order_id:
            logging.info(f"order {order_id} placed for {exchsym[1]} successfully")
            return True
    except Exception as e:
        print_exc()
        logging.error(f"{str(e)} while placing order")
        return False
    else:
        logging.error("error while generating order#")
        return False


def read_tokens(df):
    try:
        lst = []
        lst = df.index.to_list()
        if len(lst) > 0:
            dct_with_tkns = get_tokens_from_list(lst)
            df["instrument_token"] = df.index.map(lambda x: dct_with_tkns[x])
        return df
    except Exception as e:
        print(f"{str(e)} unable to get tokens")
        print_exc()


def connect(df):
    #  make a list of instrument_tokens from df
    df_token = df[["instrument_token"]]
    lst = df_token.to_dict(orient="records")
    lst = [dct["instrument_token"] for dct in lst]
    # subscribe to websocket
    Ws = Wsocket(broker.kite, lst)
    return Ws


def get_ohl(Ws):
    resp = None
    while not resp:
        resp: List[Dict] = Ws.ticks
        sleep(1)
    return resp


def run(df):
    try:
        rows_to_remove = []
        for index, row in df.iterrows():
            if (
                row["high"] > row["close_price"]
                and row["last_price"] < row["close_price"]
            ):
                is_placed = place_order(index, row)
                if is_placed:
                    rows_to_remove.append(index)

        df.drop(rows_to_remove, inplace=True)
        print(df, "\n")
        sleep(secs)
    except Exception as e:
        remove_token(S_DATA)
        print_exc()
        logging.error(f"{str(e)} in the main loop")


def flatten_ohlc(resp: List[Dict]) -> List[Dict]:
    try:
        for dct in resp:
            dct["open"] = dct["ohlc"]["open"]
            dct["high"] = dct["ohlc"]["high"]
            dct["close"] = dct["ohlc"]["close"]
            dct.pop("ohlc")
        return resp
    except Exception as e:
        print(f"{str(e)} unable to flatten ohlc")
        print_exc()


def main():
    dump()
    df = get_holdings()
    ## preparing to get quotes
    df = read_tokens(df)
    Ws = connect(df)
    while not df.empty:
        resp = get_ohl(Ws)
        print(resp)
        sleep(5)
        resp = flatten_ohlc(resp)
        resp_df = pd.DataFrame(resp)
        df = df.merge(resp_df, on="instrument_token", how="left")
        # drop columns that are not required
        dropped_colmns = ["last_price", "open", "high", "close"]
        df.drop(dropped_colmns, axis=1, inplace=True)
        print(df.columns)

        df.to_csv(S_DATA + "temp.csv", index=False)
        print(df)
        # run(df)


main()
