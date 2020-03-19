# -*- coding: utf-8 -*-
import re
import logging
from pathlib import Path
from datetime import datetime

import click
import pandas as pd

from ecdc import download_latest_data


def read_dpc_csv(filename):
    df = pd.read_csv(filename, encoding="utf-8", parse_dates=["data"])

    return df.rename(
        columns={
            "denominazione_regione": "regione",
            "denominazione_provincia": "provincia",
        }
    )


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath=Path("./data/raw"), output_filepath=Path("./data/processed")):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info("Making final data set from raw data")

    pd.set_option("io.hdf.default_format", "table")
    store = pd.HDFStore(Path(output_filepath) / "data.h5")

    logger.info("Processing ECDC data")
    data_path = Path(input_filepath) / "ecdc"
    logger.info("Downloading latest ECDC data")
    download_latest_data(data_path)
    _, file_path = max((f.stat().st_mtime, f) for f in data_path.iterdir())
    logger.info(f"Latest file: {file_path}")
    df = pd.read_excel(file_path).rename(
        columns={"Countries and territories": "Country"}
    )
    df["TotalCases"] = (
        df.iloc[::-1].groupby("Country")["Cases"].transform(pd.Series.cumsum)
    )
    df["TotalDeaths"] = (
        df.iloc[::-1].groupby("Country")["Deaths"].transform(pd.Series.cumsum)
    )
    df["Country"] = df.Country.str.replace("_", " ")
    store[f"ECDC"] = df

    logger.info("Processing Johns Hopkins CSSE data")
    data_path = (
        Path(input_filepath) / "COVID-19/csse_covid_19_data/csse_covid_19_time_series"
    )

    csse_datasets = []
    for dataset in ["Confirmed", "Deaths", "Recovered"]:
        original_df = pd.read_csv(
            data_path / f"time_series_19-covid-{dataset}.csv"
        ).drop(["Lat", "Long"], axis="columns")
        long_df = pd.melt(original_df, ["Country/Region", "Province/State"])
        long_df.columns = ["Country", "Province", "Date", dataset]
        long_df["Date"] = pd.to_datetime(long_df.Date)
        csse_datasets.append(long_df.set_index(["Date", "Country", "Province"]))
        store[f"TimeSeries{dataset}"] = long_df

    store[f"CSSE"] = csse_datasets[0].join(csse_datasets[1:]).reset_index()

    logger.info("Processing Protezione Civile original data")
    data_path = Path(input_filepath) / "protezione-civile"

    logger.info("Processing Protezione Civile original data - National")
    store["dpc_nazionale"] = read_dpc_csv(
        data_path
        / "dati-andamento-nazionale"
        / "dpc-covid19-ita-andamento-nazionale.csv"
    )
    logger.info("Processing Protezione Civile original data - Provinces")
    store["dpc_province"] = read_dpc_csv(
        data_path / "dati-province" / "dpc-covid19-ita-province.csv"
    ).rename(
        columns={
            "denominazione_regione": "regione",
            "denominazione_provincia": "provincia",
        }
    )
    logger.info("Processing Protezione Civile original data - Regions")
    reg_df = read_dpc_csv(
        data_path / "dati-regioni" / "dpc-covid19-ita-regioni.csv"
    ).rename(columns={"denominazione_regione": "regione"})
    store["dpc_regioni"] = reg_df

    reg_df = reg_df.rename(
        columns={
            "ricoverati_con_sintomi": "Ricoverati con sintomi",
            "terapia_intensiva": "ICU",
            "isolamento_domiciliare": "Isolamento domiciliare",
            "dimessi_guariti": "Guariti",
            "deceduti": "Deceduti",
        }
    ).drop(
        [
            col
            for col in reg_df.columns
            if "totale" in col or "nuovi" in col or "tampon" in col
        ],
        axis=1,
    )

    reg_long_df = pd.melt(
        reg_df,
        id_vars=reg_df.columns[:6],
        value_vars=reg_df.columns[6:],
        var_name="status",
    )
    store["dpc_regioni_long"] = reg_long_df


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
