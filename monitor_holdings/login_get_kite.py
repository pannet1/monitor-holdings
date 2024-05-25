from constants import logging, CNFG, FUTL, dir_path
import os


def get_kite():
    if CNFG["broker"] == "bypass":
        logging.debug("trying login BYPASS ..")
        kite = _get_bypass()
    else:
        print("trying login ZERODHA ..")
        kite = _get_zerodha()
        # kite = Zerodha()
    return kite


def _get_bypass():
    try:
        from omspy_brokers.bypass import Bypass

        dct = CNFG["bypass"]
        tokpath = dir_path + dct["userid"] + ".txt"
        enctoken = None
        if not FUTL.is_file_not_2day(tokpath):
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
        tokpath = dir_path + dct["userid"] + ".txt"
        zera = Zerodha(
            userid=dct["userid"],
            password=dct["password"],
            totp=dct["totp"],
            api_key=dct["api_key"],
            secret=dct["secret"],
        )
        if not FUTL.is_file_not_2day(tokpath):
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


def remove_token(dir_path):
    dct = CNFG["bypass"]
    tokpath = dir_path + dct["userid"] + ".txt"
    os.remove(tokpath)


def Zerodha():
    import requests
    import pyotp
    from kiteconnect import KiteConnect
    import sys

    dct = CNFG["zerodha"]
    logging.debug(dct)
    user_id = dct["userid"]
    password = dct["password"]
    totp = dct["totp"]
    api_key = dct["api_key"]
    secret = dct["secret"]
    tokpath = dir_path + dct["userid"] + ".txt"

    LOGINURL = "https://kite.zerodha.com/api/login"
    TWOFAURL = "https://kite.zerodha.com/api/twofa"

    try:
        session = requests.Session()
        session_post = session.post(
            LOGINURL, data={"user_id": user_id, "password": password}
        ).json()
        logging.debug(f"{session_post=}")
        if (
            session_post
            and isinstance(session_post, dict)
            and session_post["data"].get("request_id", False)
        ):
            request_id = session_post["data"]["request_id"]
            logging.debug(f"{request_id=}")
        else:
            raise ValueError("Request id is not found")
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        sys.exit(1)  # Exit with a non-zero status code to indicate an error
    except requests.RequestException as re:
        logging.error(f"RequestException: {re}")
        sys.exit(1)
    except Exception as e:
        # Handle other unexpected exceptions
        logging.exception(f"An unexpected error occurred: {e}")
        sys.exit(1)

    try:
        data = {
            "user_id": user_id,
            "request_id": request_id,
            "twofa_value": pyotp.TOTP(totp).now(),
            "skip_session": True,
        }
        response = session.post(TWOFAURL, data=data, allow_redirects=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except Exception as e:
        logging.exception(f"twofa error: {e}")
        sys.exit(1)

    try:
        data = {"api_key": api_key, "allow_redirects": True}
        session_get = session.get("https://kite.trade/connect/login/", params=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except Exception as e:
        e = str(e)
        logging.debug(f"{e=}")
        if "request_token" in e:
            request_token = e.split("request_token=")[1].split(" ")[0]
            logging.debug(f"{request_token=}")
            pass
        else:
            logging.exception(f"request token error: {e}")
            sys.exit(1)
    else:
        split_url = session_get.url.split("request_token=")
        if len(split_url) >= 2:
            request_token = split_url[1].split("&")[0]

    try:
        kite = KiteConnect(api_key=api_key)
        logging.debug(f"{data=} generated with the {request_token=}")
        data = kite.generate_session(request_token, api_secret=secret)
        if data and isinstance(data, dict) and data.get("access_token", False):
            logging.debug(f"{data['access_token']}")
            with open(tokpath, "w") as tok:
                tok.write(data["access_token"])
            return kite
        else:
            raise ValueError("Unable to generate session")
    except Exception as e:
        # Handle any unexpected exceptions
        logging.exception(f"generating session error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    kobj = get_kite()
    print(kobj.profile)
