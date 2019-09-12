#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 21:56:45 2019

@author: ianvaimberg
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pyodbc

a=pyodbc.connect('DRIVER=/Library/simba/sqlserverodbc/lib/libsqlserverodbc_sbu.dylib;'
                  'SERVER=localhost;'
                  'DATABASE=march_madness;'
                  'UID=sa;'
                  'PWD=Ivaim1997%')
cursor = a.cursor()

cursor.execute(""" SELECT r.Season, r.WTeamID, CAST(SUBSTRING(s1.Seed,2,2) AS INT) AS Win_Seed, r.LTeamID, 
CAST(SUBSTRING(s2.Seed,2,2) AS INT) AS Lose_Seed, 
m2.Centered_SOS-m1.Centered_SOS AS SOS_diff, m2.Rank_day_129-m1.Rank_day_129 AS Rank_diff, 
m1.Off_eff-m2.Off_eff AS Off_eff_diff, m1.Off_speed-m2.Off_speed AS Off_speed_diff,
m2.Def_eff-m1.Def_eff AS Def_eff_diff, m1.Def_speed-m2.Def_speed AS Def_speed_diff,
m1.Winslast10 - m2.Winslast10 AS Winslast10_diff, m1.Plus_Minus_last10 - m2.Plus_Minus_last10 AS Plus_Minus_last10_diff,
m1.FGPct - m2.FGPct AS FGPct_diff, m1.FG3Pct - m2.FG3Pct AS FG3Pct_diff, m1.FTPct - m2.FTPct AS FTPct_diff, 
m1.PFPG - m2.PFPG AS PFPG_diff, m2.PAPG - m1.PAPG AS PAPG_diff, m1.Plus_Minus - m2.Plus_Minus AS Plus_Minus_diff, 
m1.wins - m2.wins AS wins_diff, m2.Losses - m1.Losses AS Losses_diff 


FROM NCAATourneyCompactResults_ r
JOIN NCAATourneySeeds s1 ON s1.Season = r.Season AND s1.TeamID = r.WTeamID 
JOIN NCAATourneySeeds s2 ON s2.Season = r.Season AND s2.TeamID = r.LTeamID
/*WHERE r.Season >=2003
ORDER BY CAST(SUBSTRING(s2.Seed,2,2) AS INT) - CAST(SUBSTRING(s1.Seed,2,2) AS INT) DESC*/
JOIN Master_Table m1 ON r.Season = m1.Season AND r.WTeamID = m1.TeamID
JOIN Master_Table m2 ON r.Season = m2.Season AND r.LTeamID = m2.TeamID;""")

cols = ['Season','WTeamID','Win_Seed','LTeamID','Lose_Seed','SOS_diff','Rank_diff','Off_eff_diff',
           'Off_speed_diff','Def_eff_diff','Def_speed_diff','Winslast10_diff',
           'Plus_Minus_last10_diff','FGPct_diff','FG3Pct_diff', 'FTPct_diff', 
           'PFPG_diff', 'PAPG_diff','Plus_Minus_diff', 'Wins_diff','Losses_diff']

results = pd.DataFrame(np.array(cursor.fetchall()),columns=cols)
drop_cols = ['Season','WTeamID','Win_Seed','LTeamID','Lose_Seed',]

use_data = results.drop(columns= drop_cols)
#print(use_data.columns)
data_std = StandardScaler().fit_transform(use_data)

cov_mat = np.cov(data_std.T)



def sortsecond(val):
    return val[1]

eig_vals, eig_vecs = np.linalg.eig(cov_mat)
eig_pairs = [(use_data.columns[i],np.abs(eig_vals[i]),eig_vecs[:,i]) for i in range(len(eig_vals))]
eig_pairs.sort(key=sortsecond, reverse=True )


for i in eig_pairs:
    print(i[0],np.round(i[1],3))

tot = sum(eig_vals)
var_exp = [(i / tot)*100 for i in sorted(eig_vals, reverse=True)]
cum_var_exp = np.cumsum(var_exp)

all_x = np.array(eig_pairs)[:,0]

indiv_y = var_exp

cum_y = cum_var_exp

plt.subplot()

plt.bar(np.arange(len(indiv_y)),indiv_y)
plt.xticks(np.arange(len(indiv_y)),np.arange(len(indiv_y)))
plt.plot(np.arange(len(indiv_y)),cum_y)
plt.plot(np.arange(len(indiv_y)),np.linspace(95,95,len(indiv_y)))

plt.show()
