# *- coding: utf-8 -*-
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup


def download_latest_data(output_dir):
    url = r'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'

    r = requests.get(url, allow_redirects=True)
    open(output_dir / 'ecdc_latest.csv' , 'wb').write(r.content)


def ecdc_dataframe(file_path):
    df = pd.read_csv(file_path).rename(
        columns={"countriesAndTerritories": "Country"}
    )
    df["TotalCases"] = (
        df.iloc[::-1].groupby("Country")["cases"].transform(pd.Series.cumsum)
    )
    df["TotalDeaths"] = (
        df.iloc[::-1].groupby("Country")["deaths"].transform(pd.Series.cumsum)
    )
    df["TotalCasesPer1MPop"] = 1.0e6 * df.TotalCases / df.popData2019
    df["TotalDeathsPer1MPop"] = 1.0e6 * df.TotalDeaths / df.popData2019
    df["CasesPer1MPop"] = 1.0e6 * df.cases / df.popData2019
    df["DeathsPer1MPop"] = 1.0e6 * df.deaths / df.popData2019
    df["Lethality"] = 100.0 * df.TotalDeaths / df.TotalCases
    df["Country"] = df.Country.str.replace("_", " ")
    df["Date"] = pd.to_datetime(df.dateRep, format="%d/%m/%Y")
    return df