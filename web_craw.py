import requests
from bs4 import BeautifulSoup
import numpy as np

page = 1

URL = "http://cekfakta.com/page/1"
r = requests.get(URL)

soup = BeautifulSoup(r.content, 'html.parser')
weblinks = soup.find_all('li', class_="card")
print(weblinks)

pglinks = []

for li in weblinks:
    url = li.find_all('a')[0].get('href')
    pglinks.append(url)

    # print(pglinks)

    file = open('from_cekfakta/tes.txt', 'a+')
