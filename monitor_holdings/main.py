from login_get_kite import get_kite
import pandas as pd

dir_path = "../../../"
broker = get_kite(api="bypass", sec_dir=dir_path)
resp = broker.kite.holdings()
if any(resp):
    df = pd.DataFrame(resp)
    selected_cols = ['tradingsymbol', 'exchange', 'instrument_token',
                     'quantity', 'realised_quantity', 'average_price', 'pnl']
    df = df[selected_cols]
    print(df)
