from toolkit.logger import Logger
from toolkit.currency import round_to_paise
from toolkit.utilities import Utilities
from login_get_kite import get_kite
from constants import dir_path, fileutils, buff
from positions import get
from trendlyne import Trendlyne
import pandas as pd
import traceback
import sys

logging = Logger(10)
holdings = dir_path + "holdings.csv"

try:
    broker = get_kite(api="bypass", sec_dir=dir_path)
    if fileutils.is_file_not_2day(holdings):
        logging.debug("getting holdings for the day ...")
        resp = broker.kite.holdings()
        df = get(resp)
        logging.debug(f"writing to csv ... {holdings}")
        df.to_csv(holdings, index=False)
except Exception as e:
    print(traceback.format_exc())
    logging.error(f"{str(e)} unable to get holdings")
    sys.exit(1)


try:
    logging.debug(f"reading from csv ...{holdings}")
    df_holdings = pd.read_csv(holdings)
    if not df_holdings.empty:
        lst = df_holdings['tradingsymbol'].to_list()
    else:
        lst = []

    # get list from Trendlyne
    lst_dct_tlyne = Trendlyne().entry()
    lst_tlyne = [dct['tradingsymbol'] for dct in lst_dct_tlyne]
except Exception as e:
    print(traceback.format_exc())
    logging.error(f"{str(e)} unable to read holdings or Trendlyne calls")
    sys.exit(1)

try:
    if lst_tlyne and any(lst_tlyne):
        logging.debug(f"reading from trendlyne ...{lst_tlyne}")
        lst_tlyne = [
            x for x in lst_tlyne if x not in lst]
        logging.debug(f"filtered from holdings: {lst_tlyne}")

        # get list from positions
        lst_dct = broker.positions
        if lst_dct and any(lst_dct):
            lst = [dct['tradingsymbol'] for dct in lst_dct]
            lst_tlyne = [
                x for x in lst_tlyne if x not in lst]
            logging.debug(f"filtered from positions ...{lst_tlyne}")
except Exception as e:
    print(traceback.format_exc())
    logging.error(f"{str(e)} unable to read positions")
    sys.exit(1)


def transact(dct):
    def get_ltp():
        ltp = 0
        key = "NSE:" + dct['tradingsymbol']
        resp = broker.kite.ltp(key)
        if resp and isinstance(resp, dict):
            ltp = resp[key]['last_price']
            return ltp

    ltp = get_ltp()
    order_id = broker.order_place(
        tradingsymbol=dct['tradingsymbol'],
        exchange='NSE',
        transaction_type='BUY',
        quantity=int(float(dct['calculated'])),
        order_type='LIMIT',
        product='CNC',
        variety='regular',
        price=round_to_paise(ltp, buff)
    )
    if order_id:
        logging.info(
            f"BUY {order_id} placed for {dct['tradingsymbol']} successfully")
        order_id = broker.order_place(
            tradingsymbol=dct['tradingsymbol'],
            exchange='NSE',
            transaction_type='SELL',
            quantity=int(float(dct['calculated'])),
            order_type='LIMIT',
            product='CNC',
            variety='regular',
            price=round_to_paise(ltp, dct['res_3'], "sub")
        )
        if order_id:
            logging.info(
                f"SELL {order_id} placed for {dct['tradingsymbol']} successfully")
    else:
        logging.error(f"unable to place order for {dct['tradingsymbol']}")


if any(lst_tlyne):
    # Filter the original list based on the subset of 'tradingsymbol' values
    lst_orders = [d for d in lst_dct_tlyne if d['tradingsymbol'] in lst_tlyne]
    for d in lst_orders:
        transact(d)
        Utilities().slp_til_nxt_sec()
