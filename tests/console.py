import requests
from bs4 import BeautifulSoup
import traceback

"""
{
	"Request Cookies": {

		"user_id": "DK4219", 
		"enctoken": "yi5sXoyIVJjHrF5bMSzC6gcfdgulfEWWVdtOT1B0mdPtXvAOPwlM1UAdi34IU/YItxTpkHzmVLDg8Jl4jAb0yXOjHZUT//bf+2+nUQAw5taTDXTM7DAFFA==",
		"kf_session": "BqmfIuUFEYd1jvswarBUaJKQqTpKpXgU",
		"public_token": "537UangZSHuS66sunjoIF6VnXKMfjTww",
		"_cfuvid": "aMwUcK1x7Eaw8Afyx3Jqxswa0Y4NsvHd5Qu2uhAXOec-1693766339340-0-604800000",
	}
}

"""


class Console:

    base_url = "https://console.zerodha.com"
    entry_url = base_url + "/reports/pnl/"

    def __init__(self):
        fake_response = requests.get(self.base_url)
        fake_cookies = fake_response.cookies
        for cook in fake_cookies:
            print(f"{cook.name}: {cook.value}")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "Referer": self.base_url,  # Replace with the correct referer URL
            # "Cookie": "csrftoken={}".format(csrf_token),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site"
        }


if __name__ == "__main__":
    c = Console()
