import requests
from bs4 import BeautifulSoup

url = "https://trendlyne.com/fundamentals/v1/stock-screener/386853/algo-entry/"
headers = {
    "Referer": "https://trendlyne.com",  # Replace with the correct referer URL
    # Replace with the actual cookie value
    "Cookie": "csrftoken=CVGZ7FL0nllXURj3pYohKigoBh762pVTvNniMFAQjCvTbXcUc2xieW0DitN1TPy0",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site"
}

r = requests.get(url, headers=headers)

if r.status_code == 200:
    soup = BeautifulSoup(r.content, 'html5lib').prettify()
    main = soup.find('main')
    print(main)
else:
    print("Request failed with status code:", response.status_code)


"""
<main>
       <div class="table-responsive">
        <table class="table tl-dataTable stockdd tableFetch JS_autoDataTables datatable-sticky-header" data-customdom="lrtip" data-initialorder='[1, "
desc"]' data-screenpk="386853" data-searchbar="enable" width="100%">
"""
