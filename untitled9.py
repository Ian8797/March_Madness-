#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 12:56:12 2019

@author: ianvaimberg

This file made a master table from all stats used in investigation 
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



#print(sch)

SOS = pd.read_hdf("SOS.h5",str(1)).reset_index(drop=True)
last_day_rank = pd.read_hdf("Last_day_rank.h5",str(1)).reset_index(drop=True)
Eff = pd.read_hdf("Eff_data_norm.h5",str(1)).reset_index(drop=True)
Last10 = pd.read_hdf("Last10info_norm.h5",str(1)).reset_index(drop=True)
Pg = pd.read_hdf("wnL_FG_FG3_etc_norm.h5",str(1)).reset_index(drop=True)

t_names = {'SOS': SOS,'last_day_rank':last_day_rank ,'Eff': Eff,'Last10': Last10,'Pg': Pg}

col1 = t_names['SOS'].columns
col2 = t_names['last_day_rank'].columns
col3 = t_names["Eff"].columns
col4 = t_names['Last10'].columns
col5 = t_names['Pg'].columns

#print(col1,col2,col3,col4,col5)  
all_data = {'Season': SOS["Season"], 'TeamID': SOS["Team"], 'Centered_SOS': SOS["Centered_SOS"],
            'Rank_Day_129': last_day_rank["Rank_day_129"], 'Tourney_wins' : Pg['Tourney_wins'],
            'Off_eff' : Eff['Off_eff'], 'Off_speed' : Eff['Off_speed'], 'Def_eff' : Eff['Def_eff'],
            'Def_speed' : Eff['Def_speed'], 'Winslast10' : Last10['Winslast10'], 'Plus/Minus_last10' :
                Last10['Plus/Minus Last Ten'], 'FGPct' : Pg['FGPct'],'FG3Pct' : Pg['FG3Pct'], 
                'FTPct' : Pg['FTPct'], 'PFPG': Pg['PFPG'],'PAPG': Pg['PAPG'], 'Plus/Minus' : Pg['Plus/Minus'], 'Wins' : Pg['Wins'],
                'Losses' : Pg['Losses'] }  
master = pd.DataFrame(all_data)

#for x in master.columns:
    #print(master[x].isnull().sum())
master.to_hdf("Master_data.h5",str(1))


