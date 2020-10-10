from pathlib import Path
import re
from datetime import datetime

from loguru import logger
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pyprojroot import here
import camelot
from tika import parser

from istat import build_province_df
from dpc import calculate_per_1M_pop

def add_base_url(url):
    if not url.startswith("https://"):
        return f"https://www.larena.it{url}"

    return url


def get_all_pdf_links():
    URL = (
        r"https://www.larena.it/territori/citt%C3%A0/verona-dati-coronavirus-1.7976616"
    )

    logger.info('Scraping all PDF links from webpage...')
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, "html.parser")

    return [
        add_base_url(link.get("href"))
        for link in soup.find_all("a")
        if link.get("href").endswith(".pdf")
    ]


def clean_filename(fname):
    return fname.replace("%20", "_").replace("-", "").replace(" ", "_")


def download_links(to=here("./data/raw/veneto")):
    for link in get_all_pdf_links():
        out_path = Path(to) / clean_filename(Path(link).name)
        if not out_path.exists():
            logger.info(f'Downloading file {link}')
            r = requests.get(link)
            with open(out_path, "wb") as file:
                file.write(r.content)


def daily_csv_path(date):
    return Path(here(f'./data/processed/veneto/daily_{date.strftime("%y%m%d_%H%M")}.csv'))


def parse_pdf(pdf_file):
    logger.info(f'Processing file {pdf_file}')
    content = parser.from_file(str(pdf_file))['content']

    try:
        line = next(line for line in content.splitlines() if 'REPORT' in line)
        regex = re.compile(r'report del ([\d\.]+) ore ([\d\.]+)', re.IGNORECASE)
    except:
        logger.warning('Normal regular expression failed. Trying with backup.')
        line = next(line for line in content.splitlines() if line.startswith('CASI SARS'))
        regex = re.compile(r'casi sars.* ([\d\.]+) ore ([\d\.]+) ', re.IGNORECASE)
        
    try:
        m = re.match(regex, line.replace('-', '.'))
        giorno, mese = (int(value) for value in m.group(1).split('.'))
        ora, minuto = (int(value) for value in m.group(2).split('.'))
        data = datetime(2020, mese, giorno, ora, minuto, 0)

        if not daily_csv_path(data).exists():
            tables = camelot.read_pdf(str(pdf_file), flavor='lattice')
            df = tables[0].df
            df.columns = ['provincia', 'totale_casi', 'nuovi_positivi', 'attualmente_positivi', 'deceduti', 'negativizzati'][:len(df.columns)]
            df['data'] = data
            df[1:-1].to_csv(daily_csv_path(data))
        
    except:
        raise ValueError(f"Cannot parse {pdf_file}")

def create_dataset():
    base_path = here("./data/raw/veneto")
    
    for file in base_path.glob('*.pdf'):
        parse_pdf(file)

    processed_path = Path(here("./data/processed/veneto"))

    logger.info('Merging all dataframes and writing to CSV...')
    df = pd.concat((pd.read_csv(csv_file) for csv_file in processed_path.glob('*.csv')), sort=False)
    df = df.rename(columns={df.columns[0]: "codice" })
    df.loc[df.codice == 1, 'provincia'] = 'Padova'
    df.loc[df.codice == 2, 'provincia'] = 'Padova'
    veneto = df.groupby(['data', 'provincia']).sum().drop('codice', axis=1).reset_index()
    istat = pd.read_csv(here('./data/raw/istat/popolazione/DCIS_POPRES1_06052020222758332.csv'))
    istat = istat[(istat.STATCIV2 == 99) & (istat.ETA1 == 'TOTAL') & (istat.SEXISTAT1 == 9)][['ITTER107', 'Territorio', 'Value']].rename(columns={'Value': 'popolazione'})
    province = istat[istat.ITTER107.str.match(r'IT\w\d\d\b')].drop('ITTER107', axis=1)
    merged = veneto.merge(province, left_on='provincia', right_on='Territorio').drop('Territorio', axis=1)
    diffs = merged.groupby('provincia').diff()
    diffs.columns = ['nuovi_positivi', 'variazione_totale_positivi', 'nuovi_deceduti', 'nuovi_negativizzati', 'drop']
    diffs = diffs.drop('drop', axis=1)
    calculate_per_1M_pop(pd.merge(merged, diffs, left_index=True, right_index=True)).to_csv(Path(here("./data/processed/veneto.csv")))

if __name__ == "__main__":
    download_links()
    create_dataset()
