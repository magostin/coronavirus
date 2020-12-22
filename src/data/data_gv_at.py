import requests
import pandas as pd

BASE_URL = "https://covid19-dashboard.ages.at/data/"

FILES = [
    "CovidFaelle_Timeline_GKZ.csv",
    "CovidFaelle_Timeline.csv",
    "CovidFaelle_GKZ.csv",
    "CovidFallzahlen.csv",
]

BUNDESLAENDER = {
    1: "Burgenland",
    2: "Kärnten",
    3: "Niederösterreich",
    4: "Oberösterreich",
    5: "Salzburg",
    6: "Steiermark",
    7: "Tirol",
    8: "Vorarlberg",
    9: "Wien",
}


def austria_data():
    df = pd.read_csv(BASE_URL + "CovidFaelle_Timeline.csv", sep=";", decimal=",")
    zahlen = pd.read_csv(BASE_URL + "CovidFallzahlen.csv", sep=";", decimal=",")
    zahlen["Date"] = pd.to_datetime(zahlen.MeldeDatum, format="%d.%m.%Y %H:%M:%S")
    df["Date"] = pd.to_datetime(df.Time, format="%d.%m.%Y %H:%M:%S")
    df["RollingAvg"] = df.AnzahlFaelle7Tage / 7
    df["Incidence"] = 10 * df.SiebenTageInzidenzFaelle / 7
    df = df.merge(zahlen, on=["Date", "BundeslandID"], how="left")
    return df


def austria_gkz():
    df = pd.read_csv(BASE_URL + "CovidFaelle_GKZ.csv", sep=";", decimal=",")
    df["BundeslandID"] = df.GKZ // 100
    df["Bundesland"] = df.BundeslandID.replace(BUNDESLAENDER)
    df["Incidence"] = 1e6 * df.AnzahlFaelle7Tage / 7 / df.AnzEinwohner
    return df
