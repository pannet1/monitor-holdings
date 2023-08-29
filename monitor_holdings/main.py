from toolkit.logger import Logger
from toolkit.currency import round_to_paise
from login_get_kite import get_kite, remove_token
import sys
from time import sleep
import traceback
from constants import dir_path, buff, secs, perc_col_name
from holdings import get

logging = Logger(30, dir_path + "main.log")
try:
    broker = get_kite(api="bypass", sec_dir=dir_path)
    logging.debug("getting holdings for the day ...")
    resp = broker.kite.holdings()
    df = get(resp)
except Exception as e:
    remove_token(dir_path)
    print(traceback.format_exc())
    logging.error(f"{str(e)} unable to get holdings")
    sys.exit(1)

try:
    lst = []
    logging.debug("filtering for required columns")
    df['key'] = df['exchange'] + ":" + df['tradingsymbol']
    df.set_index('key', inplace=True)
    df = df[df[perc_col_name] != False]
    df.drop(['exchange', 'tradingsymbol', 'average_price', 'last_price',
            'unrealized', 'cap', perc_col_name], axis=1, inplace=True)
    lst = df.index.to_list()
except Exception as e:
    print(traceback.format_exc())
    logging.error(f"{str(e)} while reading from csv")
    sys.exit(1)


def order_place(index, row):
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
            price=round_to_paise(row['ltp'], buff)
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
        dct = {k: {'ltp': v['last_price'],
                   'open': v['ohlc']['open'],
                   'high': v['ohlc']['high'],
                   'low': v['ohlc']['low'],
                   }
               for k, v in resp.items()}
        df['ltp'] = df.index.map(lambda x: dct[x]['ltp'])
        df['open'] = df.index.map(lambda x: dct[x]['open'])
        df['high'] = df.index.map(lambda x: dct[x]['high'])
        df['low'] = df.index.map(lambda x: dct[x]['low'])

        rows_to_remove = []
        for index, row in df.iterrows():
            if row['high'] > row['close_price'] and row['ltp'] < row['close_price']:
                is_placed = order_place(index, row)
                if is_placed:
                    rows_to_remove.append(index)

        df.drop(rows_to_remove, inplace=True)
        print(df, "\n")
        sleep(secs)
    else:
        logging.info("there is no holdings to process ... exiting")
        sys.exit(0)
except Exception as e:
    remove_token(dir_path)
    print(traceback.format_exc())
    logging.error(f"{str(e)} in the main loop")
