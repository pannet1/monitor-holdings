from toolkit.logger import Logger
from login_get_kite import get_kite, remove_token
import sys
import traceback
from constants import S_DATA
import pandas as pd


logging = Logger(10)
try:
    broker = get_kite()
    logging.debug("getting margins ...")
    dct_mgn = broker.kite.margins().get("equity", {})
    print(pd.DataFrame(dct_mgn))
except Exception as e:
    remove_token(S_DATA)
    print(traceback.format_exc())
    logging.error(f"{str(e)} unable to get holdings")
    sys.exit(1)
