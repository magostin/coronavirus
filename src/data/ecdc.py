# *- coding: utf-8 -*-
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup


def download_latest_data(output_dir):
    url = r'https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide'

    r = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(r.text, 'html.parser')

    link = soup.find('a', attrs={'href': re.compile("^https://.*xls")}).get('href')
    
    r = requests.get(link, allow_redirects=True)   
    open(output_dir / Path(urlparse(link).path).name , 'wb').write(r.content)


def ecdc_dataframe(file_path):
    df = pd.read_excel(file_path).rename(
        columns={"countriesAndTerritories": "Country"}
    )
    df["TotalCases"] = (
        df.iloc[::-1].groupby("Country")["cases"].transform(pd.Series.cumsum)
    )
    df["TotalDeaths"] = (
        df.iloc[::-1].groupby("Country")["deaths"].transform(pd.Series.cumsum)
    )
    df["TotalCasesPer1MPop"] = 1.0e6 * df.TotalCases / df.popData2018
    df["TotalDeathsPer1MPop"] = 1.0e6 * df.TotalDeaths / df.popData2018
    df["CasesPer1MPop"] = 1.0e6 * df.cases / df.popData2018
    df["DeathsPer1MPop"] = 1.0e6 * df.deaths / df.popData2018
    df["Lethality"] = 100.0 * df.TotalDeaths / df.TotalCases
    df["Country"] = df.Country.str.replace("_", " ")
    df["Date"] = pd.to_datetime(df.dateRep, format="%d/%m/%Y")
    return df