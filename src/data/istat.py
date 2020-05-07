import numpy as np
import pandas as pd

def build_regioni_df(regioni_df, codici):
    codici_regione = codici.groupby(['Denominazione regione', 'Codice Regione']).size().reset_index()
    codici_regione.columns = ['denominazione', 'codice_regione', 'Count']
    regioni = regioni_df.set_index('Territorio').join(codici_regione.set_index('denominazione'))
    regioni.loc["Valle d'Aosta / Vallée d'Aoste", 'codice_regione'] = 2
    regioni.loc["Provincia Autonoma Trento", 'codice_regione'] = 41
    regioni.loc["Provincia Autonoma Bolzano / Bozen", 'codice_regione'] = 42
    return regioni.reset_index()

def build_province_df(province, codici):
    codici_provincia = codici.groupby(["Denominazione dell'Unità territoriale sovracomunale \n(valida a fini statistici)", 'Codice Provincia (Storico)(1)']).size().reset_index()
    codici_provincia.columns = ['denominazione', 'codice_provincia', 'Count']
    province.loc[:, 'Territorio'] = province.Territorio.str.replace(' / ', '/')
    province.loc[:, 'Territorio'] = province.Territorio.str.replace('Reggio di Calabria', 'Reggio Calabria')
    province_joined = province.set_index('Territorio').join(codici_provincia.set_index('denominazione'))
    return province_joined.reset_index()

def aggiorna_codice_regione(row):
    if 'Trento' in row.regione:
        return 41
    
    if 'Bolzano' in row.regione:
        return 42
    
    return row.codice_regione