#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 15:13:54 2019

@author: ianvaimberg

This file investigates 1 varible correlation between team stats and tourney wins -- 
found nothing because not scaled for strength of teams playing 

showed meaningful correlation between SOS and tourney wins, 
need 60% threshold to make final 3 rounds
"""

import pyodbc
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd

 
a=pyodbc.connect('DRIVER=/Library/simba/sqlserverodbc/lib/libsqlserverodbc_sbu.dylib;'
                  'SERVER=localhost;'
                  'DATABASE=march_madness;'
                  'UID=sa;'
                  'PWD=Ivaim1997%')
                  
cursor = a.cursor()

table = 'NCAATourneyDetailedResults_'
table2 = 'RegularSeasonDetailedResults_'

stats2 = 'FTA'
stats= 'FTM'

cursor.execute("""WITH wins_table AS (SELECT Season, WTeamID, COUNT(WTeamID) 
                AS wins FROM NCAATourneyDetailedResults_
                GROUP BY Season, WTeamID), 
                
                win_stats AS (SELECT Season, WTeamID, SUM(W"""+stats+""") AS FTM, SUM(W"""+stats2+""") AS FTA,
                COUNT(WTeamID) AS wins FROM RegularSeasonDetailedResults_
                GROUP BY Season, WTeamID),

                loss_stats AS (SELECT Season, LTeamID, SUM(L"""+stats+""") AS FTM, SUM(L"""+stats2+""") AS FTA,
                COUNT(LTeamID) AS losses FROM RegularSeasonDetailedResults_
                GROUP BY Season, LTeamID),
                
                stat_table  AS (SELECT w.Season AS Season, w.WTeamID AS team, 
                CAST((w.FTM + l.FTM) AS FLOAT) / CAST((w.FTA + l.FTA) AS FLOAT) AS PM , w.wins AS wins, 
                l.losses AS losses  FROM win_stats w 
                JOIN loss_stats l ON w.WTeamID = l.LTeamID AND w.Season = l.Season)
                
                SELECT s.Season, s.PM, w.wins, s.wins, s.losses, w.WTeamID FROM 
                stat_table s JOIN wins_table w 
                ON w.WTeamID = s.team AND w.Season = s.Season 
                WHERE s.Season >= 2003 """)
                
                
result = cursor.fetchall()
data = np.array(result)
print(data)

tourney_sos = np.zeros(data.shape[0])
team_sos = pd.read_hdf("Exp_SOS.h5",str(1))

for i, row in enumerate(data):
    tourney_sos[i] = team_sos[(team_sos['Season'] == row[0]) & 
               (team_sos['Team'] == row[5])]['EXP_SOS_2']

#print(tourney_sos)

wins = data[:,2]
stat = data[:,1]

fit = np.polyfit(wins,stat , 1)
fit_fn = np.poly1d(fit)

plt.scatter(stat,wins)
#plt.plot(wins, fit_fn(wins), '--o')
plt.show()
    




