import pandas as pd
from pyprojroot import here


def get_processed_dataset(name):
    store = pd.HDFStore(here("./data/processed/data.h5"))
    df = store[name]
    store.close()
    return df 
