# -*- coding: utf-8 -*-
import re
import logging
from pathlib import Path
from datetime import datetime

import click
import pandas as pd

from ecdc import download_latest_data, ecdc_dataframe
from dpc import add_calc, calculate_per_1M_pop, prov_per_1M_pop
from istat import build_regioni_df, build_province_df
from data_gv_at import austria_data, austria_gkz

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
    hdf_file = Path(output_filepath) / "data.h5"

    # logger.info("Processing ECDC data")
    # data_path = Path(input_filepath) / "ecdc"
    # logger.info("Downloading latest ECDC data")
    # download_latest_data(data_path)
    # _, file_path = max((f.stat().st_mtime, f) for f in data_path.iterdir())
    # logger.info(f"Latest file: {file_path}")
    # ecdc_df = ecdc_dataframe(file_path)
    # logger.info(f"ECDC latest update: {ecdc_df.Date.max()}")
    # ecdc_df.to_hdf(hdf_file, "ECDC")

    logger.info("Processing ISTAT original data")
    istat = pd.read_csv(Path(input_filepath) / 'istat/popolazione/DCIS_POPRES1_06052020222758332.csv')
    istat = istat[(istat.STATCIV2 == 99) & (istat.ETA1 == 'TOTAL') & (istat.SEXISTAT1 == 9)][['ITTER107', 'Territorio', 'Value']].rename(columns={'Value': 'popolazione'})
    codici = pd.read_csv(Path(input_filepath) / 'istat/codici/Elenco-codici-statistici-e-denominazioni-al-01_01_2020.csv', encoding='Latin-1', sep=';').rename(columns={'NUTS2(3) ': 'NUTS2'})
    regioni = build_regioni_df(istat[istat.ITTER107.str.match(r'IT\w\d\b')], codici)[['codice_regione', 'popolazione']]
    province = build_province_df(istat[istat.ITTER107.str.match(r'IT\w\w\w\b')], codici)[['codice_provincia', 'popolazione']]

    logger.info("Processing Protezione Civile original data")
    data_path = Path(input_filepath) / "protezione-civile"

    logger.info("Processing Protezione Civile original data - National")
    naz_df = read_dpc_csv(
        data_path
        / "dati-andamento-nazionale"
        / "dpc-covid19-ita-andamento-nazionale.csv"
    )
    naz_df = naz_df.join(add_calc(naz_df))
    naz_df['incidenza'] = naz_df['nuovi_positivi'].rolling(7).mean() * 1e6 / 60359546
    naz_df.to_hdf(hdf_file, "dpc_nazionale")
    logger.info("Processing Protezione Civile original data - Provinces")
    prov_df = read_dpc_csv(
        data_path / "dati-province" / "dpc-covid19-ita-province.csv"
    ).rename(
        columns={
            "denominazione_regione": "regione",
            "denominazione_provincia": "provincia",
        }
    )
    prov_df = pd.merge(prov_df, province, on="codice_provincia")
    prov_per_1M_pop(prov_df).to_hdf(hdf_file, "dpc_province")

    logger.info("Processing Protezione Civile original data - Regions")
    reg_df = read_dpc_csv(
        data_path / "dati-regioni" / "dpc-covid19-ita-regioni.csv"
    ).rename(columns={"denominazione_regione": "regione"})
    reg_df.to_hdf(hdf_file, "dpc_regioni_raw")
    reg_df = pd.merge(reg_df, regioni, on='codice_regione')
    reg_df = reg_df.join(reg_df.groupby('regione').apply(add_calc))
    calculate_per_1M_pop(reg_df).to_hdf(hdf_file, "dpc_regioni")

    logger.info("Processing Open Data Österreich data")
    austria_data().to_hdf(hdf_file, "austria_country")
    austria_gkz().to_hdf(hdf_file, "austria_gkz")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
