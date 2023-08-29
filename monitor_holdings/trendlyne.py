import requests
from bs4 import BeautifulSoup
import traceback


class Trendlyne:

    base_url = "https://trendlyne.com"
    entry_url = base_url + "/fundamentals/v1/stock-screener/386853/algo-entry/"

    def __init__(self):
        fake_response = requests.get(self.base_url)
        fake_cookies = fake_response.cookies
        csrf_token = fake_cookies.get('csrftoken')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "Referer": self.base_url,  # Replace with the correct referer URL
            # Replace with the actual cookie value
            "Cookie": "csrftoken={}".format(csrf_token),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site"
        }

    def entry(self):
        try:
            r = requests.get(self.entry_url, headers=self.headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                maintag = soup.find(name='main')
                tbody = maintag.find(name='tbody')
                data_list = tbody.find_all(name='span', attrs={
                    'class': 'column-value'})
                # Extract the inner content using .get_text() method
                inner_contents = [span.get_text(strip=True).replace(
                    '%', '') for span in data_list]
                inner_contents = [content.replace('\n', '').replace(
                    ' ', '') for content in inner_contents]
                # Separate the list into rows with 8 fields each
                rows = [inner_contents[i:i+9]
                        for i in range(0, len(inner_contents), 9)]

                # Convert separated data into a list of dictionaries
                data_list_of_dicts = []
                for row in rows:
                    data_dict = {
                        'fall': row[0],
                        'tradingsymbol': row[1],
                        'calculated': row[2],
                        'ltp': row[3],
                        'piv': row[4],
                        'res_1': row[5],
                        'res_2': row[6],
                        'res_3': row[7],
                        'upside': row[8]
                    }
                    data_list_of_dicts.append(data_dict)
                return data_list_of_dicts
            else:
                print("Request failed with status code:", r.status_code)
        except Exception as e:
            print(traceback.format_exc())
            print(e)


if __name__ == '__main__':
    t = Trendlyne()
    print(t.entry())
