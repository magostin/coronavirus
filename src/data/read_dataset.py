import pandas as pd
from pyprojroot import here


def get_processed_dataset(name):
    return pd.read_hdf(here("./data/processed/data.h5"), name)
