
from constants import perc, perc_col_name
import pandas as pd


def get(resp):
    df = pd.DataFrame(resp)
    selected_cols = ['tradingsymbol', 'exchange', 'instrument_token',
                     'quantity', 't1_quantity', 'close_price', 'average_price']
    df = df[selected_cols]
    df['calculated'] = df['quantity'] + df['t1_quantity']
    df['cap'] = (df['calculated'] * df['average_price']).astype(int)
    df['unrealized'] = (
        (df['close_price'] - df['average_price']) * df['calculated']).round(2)
    df['perc'] = ((df['unrealized'] / df['cap']) * 100).where((df['cap']
                                                               != 0) & (df['unrealized'] != 0), 0).round(2)
    cond = f"perc > {perc}"
    df[perc_col_name] = df.eval(cond)
    print(df)
    return df
