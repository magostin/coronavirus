# -*- coding: utf-8 -*-
import re
import logging
from pathlib import Path
from datetime import datetime

import click
import pandas as pd


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath=Path("./data/raw"), output_filepath=Path("./data/processed")):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info("Making final data set from raw data")

    store = pd.HDFStore(Path(output_filepath) / "data.h5")

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
    
    store["dpc-nazionale"] = pd.read_csv(data_path / 'dati-andamento-nazionale' / 'dpc-covid19-ita-andamento-nazionale.csv')
    store["dpc-province"] = pd.concat((pd.read_csv(prov_file, encoding='latin-1') for prov_file in Path(data_path / 'dati-province').glob('*.csv')))
    reg_df = pd.concat((pd.read_csv(reg_file, encoding='latin-1') for reg_file in Path(data_path / 'dati-regioni').glob('*.csv')))
    store["dpc-regioni"] = reg_df.rename(columns={"denominazione_regione": "regione"})


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
