from toolkit.logger import Logger
from toolkit.fileutils import Fileutils
from login_get_kite import get_kite, remove_token
import pandas as pd
import sys
from time import sleep
import traceback

dir_path = "../../../"
logging = Logger(10)
fileutils = Fileutils()
holdings = dir_path + "holdings.csv"
settings_file = "settings.yaml"

try:
    logging.debug(f"read settings from {settings_file}")
    settings = fileutils.get_lst_fm_yml(settings_file)
    perc = settings['perc']
    buff = settings['buff']
    perc_col_name = f"perc_gr_{int(perc)}"
    logging.debug("create a column named after user settings {perc_col_name}")
    broker = get_kite(api="bypass", sec_dir=dir_path)
    logging.debug("getting holdings for the day ...")
    resp = broker.kite.holdings()
    df = pd.DataFrame(resp)
    selected_cols = ['tradingsymbol', 'exchange', 'instrument_token',
                     'quantity', 't1_quantity', 'close_price', 'average_price', 'pnl']
    logging.debug(f"filtering columns {str(selected_cols)}")
    df = df[selected_cols]
    logging.debug("applying necessary rules ...")
    df['calculated'] = df['quantity'] + df['t1_quantity']
    df['cap'] = (df['calculated'] * df['average_price']).astype(int)
    df['perc'] = ((df['pnl'] / df['cap']) * 100).round(2)
    df['perc'] = ((df['pnl'] / df['cap']) * 100).where((df['cap']
                                                        != 0) & (df['pnl'] != 0), 0).round(2)
    cond = f"perc > {perc}"
    df[perc_col_name] = df.eval(cond)
    print(df)
    logging.debug(f"writing to csv ... {holdings}")
    df.to_csv(holdings, index=False)
except Exception as e:
    remove_token(dir_path)
    print(traceback.format_exc())
    logging.error(f"{str(e)} unable to get holdings")
    sys.exit(1)

try:
    lst = []
    logging.debug(f"reading from csv ...{holdings}")
    df = pd.read_csv(holdings)
    logging.debug("filtering for required columns")
    df['key'] = df['exchange'] + ":" + df['tradingsymbol']
    df.set_index('key', inplace=True)
    df = df[df[perc_col_name] != False]
    df.drop(['exchange', 'tradingsymbol', 'average_price',
            'pnl', 'cap', perc_col_name], axis=1, inplace=True)
    lst = df.index.to_list()
except Exception as e:
    print(traceback.format_exc())
    logging.error(f"{str(e)} while reading from csv")
    sys.exit(1)


def order_place(index, row):
    def get_price():
        price = row['ltp'] if buff == 0 else row['ltp'] + \
            (buff / 100 * row['ltp'])
        return price

    try:
        exchsym = index.split(":")
        logging.info(f"placing order for {index}, str{row}")
        order_id = broker.order_place(
            tradingsymbol=exchsym[1],
            exchange=exchsym[0],
            transaction_type='SELL',
            quantity=int(row['calculated']),
            order_type='LIMIT',
            product='CNC',
            variety='regular',
            price=get_price()
        )
        if order_id:
            logging.info(
                f"order {order_id} placed for {exchsym[1]} successfully")
            return True
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"{str(e)} while placing order")
        return False
    else:
        logging.error("error while generating order#")
        return False


try:
    logging.debug("loop for LTP to check conditions and exit holdings")
    logging.debug("are we having any holdings to check")
    while len(lst) > 0:
        resp = broker.kite.ohlc(lst)
        dct = {k: {'ltp': v['last_price'], 'high': v['ohlc']['high']}
               for k, v in resp.items()}
        df['ltp'] = df.index.map(lambda x: dct[x]['ltp'])
        df['high'] = df.index.map(lambda x: dct[x]['high'])

        rows_to_remove = []
        for index, row in df.iterrows():
            if row['high'] > row['close_price'] and row['ltp'] < row['close_price']:
                is_placed = order_place(index, row)
                if is_placed:
                    rows_to_remove.append(index)

        df.drop(rows_to_remove, inplace=True)
        print(df, "\n")
        sleep(settings['secs'])
    else:
        logging.info("there is no holdings to process ... exiting")
        sys.exit(0)
except Exception as e:
    remove_token(dir_path)
    print(traceback.format_exc())
    logging.error(f"{str(e)} in the main loop")
