from login_get_kite import get_kite
from toolkit.logger import Logger
import pandas as pd
import sys

dir_path = "../../../"
logging = Logger(10)
broker = get_kite(api="bypass", sec_dir=dir_path)
resp = broker.kite.holdings()

try:
    df = pd.DataFrame(resp)
    print(df.columns)
    selected_cols = ['tradingsymbol', 'exchange', 'instrument_token',
                     'quantity', 'realised_quantity', 'close_price', 'average_price', 'pnl']
    df = df[selected_cols]

except Exception as e:
    logging.error(f"str{e} unable to get holdings")
    sys.exit(1)

try:
    df['key'] = df['exchange'] + ":" + df['tradingsymbol']
    df.set_index('key', inplace=True)
    df.drop(['exchange', 'tradingsymbol'], axis=1, inplace=True)
    df['cap'] = (df['quantity'] * df['average_price']).astype(int)
    df['perc'] = ((df['pnl'] / df['cap']) * 100).round(2)
    print(df)
    lst = df.index.to_list()
except Exception as e:
    logging.error(f"str{e} while calculating")
    sys.exit(1)


try:
    resp = broker.kite.ohlc(lst)
    dct = {k: {'ltp': v['last_price'], 'high': v['ohlc']['high']}
           for k, v in resp.items()}
    # Create a new column in the DataFrame to store the comparison result
    df['high_gt_close'] = df.apply(
        lambda row: dct[row.name]['high'] > row['close_price'], axis=1)
    df['close_gt_ltp'] = df.apply(
        lambda row: dct[row.name]['ltp'] < row['close_price'], axis=1)
    print(dct, "\n", df)
except Exception as e:
    logging.error(f"str{e} while interracting with broker")
