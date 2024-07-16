from constants import logging, CNFG, O_FUTL, S_DATA
import os


def get_kite():
    if CNFG["broker"] == "bypass":
        logging.debug("trying login BYPASS ..")
        kite = _get_bypass()
    else:
        print("trying login ZERODHA ..")
        kite = _get_zerodha()
    return kite


def _get_bypass():
    try:
        from omspy_brokers.bypass import Bypass

        dct = CNFG["bypass"]
        tokpath = S_DATA + dct["userid"] + ".txt"
        enctoken = None
        if not O_FUTL.is_file_not_2day(tokpath):
            print(f"{tokpath} modified today ... reading {enctoken}")
            with open(tokpath, "r") as tf:
                enctoken = tf.read()
                if len(enctoken) < 5:
                    enctoken = None
        print(f"enctoken to broker {enctoken}")
        bypass = Bypass(dct["userid"], dct["password"], dct["totp"], tokpath, enctoken)
        if bypass.authenticate():
            if not enctoken:
                enctoken = bypass.kite.enctoken
                with open(tokpath, "w") as tw:
                    tw.write(enctoken)
    except Exception as e:
        print(f"unable to create bypass object {e}")
    else:
        return bypass


def _get_zerodha():
    try:
        from omspy_brokers.zerodha import Zerodha

        dct = CNFG["zerodha"]
        tokpath = S_DATA + dct["userid"] + ".txt"
        zera = Zerodha(
            userid=dct["userid"],
            password=dct["password"],
            totp=dct["totp"],
            api_key=dct["api_key"],
            secret=dct["secret"],
        )
        if not O_FUTL.is_file_not_2day(tokpath):
            with open(tokpath, "r") as tf:
                enctoken = tf.read()
                if len(enctoken) > 5:
                    zera.kite.set_access_token(enctoken)
                    return zera
        if zera.authenticate():
            with open(tokpath, "w") as tw:
                tw.write(zera.enctoken)
            return zera
    except Exception as e:
        print(f"exception while creating zerodha object {e}")


def remove_token(S_DATA):
    dct = CNFG["bypass"]
    tokpath = S_DATA + dct["userid"] + ".txt"
    if O_FUTL.is_file_exists(tokpath):
        os.remove(tokpath)


if __name__ == "__main__":
    kobj = get_kite()
    print(kobj.profile)
