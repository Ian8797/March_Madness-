#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 14:28:28 2019

@author: ianvaimberg
"""
import pandas as pd
import pyodbc
import numpy as np

all_data = pd.read_hdf("Master_data_norm.h5",str(1))

for x in all_data.columns:
    all_data[x] = all_data[x].astype(float)

a=pyodbc.connect('DRIVER=/Library/simba/sqlserverodbc/lib/libsqlserverodbc_sbu.dylib;'
                  'SERVER=localhost;'
                  'DATABASE=march_madness;'
                  'UID=sa;'
                  'PWD=Ivaim1997%')
cursor = a.cursor()

cursor.execute("""CREATE TABLE Master_Table (
                        Season SMALLINT,
                        TeamID  SMALLINT,
                        Tourney_wins SMALLINT,
                        Centered_SOS FLOAT,
                        Rank_day_129 FLOAT,
                        Off_eff FLOAT,
                        Off_speed FLOAT,
                        Def_eff FLOAT,
                        Def_speed FLOAT,
                        Winslast10 FlOAT,
                        Plus_Minus_last10 FLOAT,
                        FGPct FLOAT,
                        FG3Pct FLOAT,
                        FTPct FLOAT,
                        PFPG FLOAT,
                        PAPG FLOAT,
                        Plus_Minus FLOAT,
                        Wins FLOAT,
                        Losses FLOAT,
                        
                        
                        )
               """)
a.commit()


def gen_rows(df):
    for row in df.itertuples(index=False):
        yield row



cursor.fast_executemany = True
cursor.executemany("""INSERT INTO Master_Table (Season, TeamID, Tourney_wins, Centered_SOS, 
                                                   Rank_day_129, Off_eff, Off_speed, Def_eff, 
                                                   Def_speed, Winslast10, Plus_Minus_last10,
                                                   FGPct, FG3Pct, FTPct, PFPG, PAPG, Plus_Minus,
                                                   Wins, Losses)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",gen_rows(all_data))

a.commit()


