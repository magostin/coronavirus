import pandas as pd

def add_calc(x):
    d = {}
    
    d['nuovi_deceduti'] = x.deceduti.diff()
    d['nuovi_tamponi'] = x.tamponi.diff()
    d['nuovi_casi_testati'] = x.casi_testati.diff()
    d['incremento'] = 100.0 * x['nuovi_positivi'] / x['totale_casi']
    d['percentuale_positivi'] = 100.0 * x['totale_casi'] / x['casi_testati']
    d['percentuale_nuovi_positivi'] = 100.0 * x['nuovi_positivi'] / d['nuovi_casi_testati']
    d['letalita'] = 100.0 * x.deceduti / x.totale_casi
    
    return pd.DataFrame(d)


def calculate_per_1M_pop(df):
    df['totale_casi_per_1M_pop'] = 1e6 * df.totale_casi / df.popolazione
    df['deceduti_per_1M_pop'] = 1e6 * df.deceduti / df.popolazione
    df['nuovi_deceduti_per_1M_pop'] = 1e6 * df.nuovi_deceduti / df.popolazione
    df['nuovi_positivi_per_1M_pop'] = 1e6 * df.nuovi_positivi / df.popolazione
    return df


def prov_per_1M_pop(df):
    df['nuovi_positivi'] = df.groupby('provincia').totale_casi.diff()
    df['incremento'] = 100.0 * df['nuovi_positivi'] / df['totale_casi']
    df['totale_casi_per_1M_pop'] = 1e6 * df.totale_casi / df.popolazione
    df['nuovi_positivi_per_1M_pop'] = 1e6 * df.nuovi_positivi / df.popolazione
    return df
