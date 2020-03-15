# *- coding: utf-8 -*-
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def download_latest_data(output_dir):
    url = r'https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide'

    r = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(r.text, 'html.parser')

    link = soup.find('a', attrs={'href': re.compile("^https://.*xls")}).get('href')
    
    r = requests.get(link, allow_redirects=True)   
    open(output_dir / Path(urlparse(link).path).name , 'wb').write(r.content)
