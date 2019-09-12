#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 10:59:04 2019

@author: ianvaimberg
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
                AS wins FROM NCAATourneyDetailedResults_ WHERE Season >=2003
                GROUP BY Season, WTeamID),

                no_wins AS (SELECT n.Season, n.TeamID AS WTeamID, 0 AS wins FROM NCAATourneySeeds n LEFT JOIN wins_table w
                ON w.Season = n.Season AND w.WTeamID = n.TeamID WHERE w.WTeamID IS NULL AND n.Season >=2003),
                
                tourney_wins AS ((SELECT * FROM wins_table) UNION (SELECT * FROM no_wins)),
                
                win_stats AS (SELECT t.Season, t.WTeamID, SUM(r.WFGM) AS FGM, SUM(r.WFGA) AS FGA,
                SUM(r.WFGM3) AS FGM3, SUM(r.WFGA3) AS FGA3, SUM(r.WFTM) AS FTM, SUM(r.WFTA) AS FTA, 
                SUM(r.WScore) AS points_for, SUM(r.LScore) AS points_against,
                COUNT(r.WTeamID) AS wins FROM RegularSeasonDetailedResults_ r RIGHT JOIN tourney_wins t 
                ON r.Season = t.Season AND r.WTeamID = t.WTeamID
                GROUP BY t.Season, t.WTeamID),
                
                loss AS (SELECT t.Season, t.WTeamID AS LTeamID, SUM(r.LFGM) AS FGM, SUM(r.LFGA) AS FGA,
                SUM(r.LFGM3) AS FGM3, SUM(r.LFGA3) AS FGA3, SUM(r.LFTM) AS FTM, SUM(r.LFTA) AS FTA, 
                SUM(r.LScore) AS points_for, SUM(r.WScore) AS points_against,
                COUNT(r.LTeamID) AS losses FROM RegularSeasonDetailedResults_ r RIGHT JOIN tourney_wins t ON 
                r.Season = t.Season AND r.LTeamID = t.WTeamID 
                GROUP BY t.Season, t.WTeamID),
                
              
                loss_stats AS (SELECT Season, LTeamID, ISNULL(FGM, 0) AS FGM, ISNULL(FGA, 0) AS FGA, 
                ISNULL(FGM3, 0) AS FGM3, ISNULL(FGA3, 0) AS FGA3, ISNULL(FTM, 0) AS FTM, 
                ISNULL(FTA, 0) AS FTA, ISNULL(points_for, 0) AS points_for, 
                ISNULL(points_against, 0) AS points_against, ISNULL(losses,0) AS losses FROM loss),
                
               

                stat_table AS (SELECT CAST(w.Season AS INT) AS Season, CAST(w.WTeamID AS INT) AS Team, 
                ROUND(CAST((w.FGM + l.FGM) AS Float) / CAST((w.FGA + l.FGA) AS Float),3) AS FGPct,
                ROUND(CAST((w.FGM3 + l.FGM3) AS Float) / CAST((w.FGA3 + l.FGA3) AS Float),3) AS FG3Pct,
                ROUND(CAST((w.FTM + l.FTM) AS Float) / CAST((w.FTA + l.FTA) AS Float),3) AS FTPct,
                ROUND(CAST(((w.points_for + l.points_for) / (w.wins +l.losses)) AS FLOAT ),1) AS PFPG, 
                ROUND(CAST((w.points_against + l.points_against) AS FLOAT) / CAST((w.wins+l.losses) AS FLOAT ),1) AS PAPG,
                (w.points_for + l.points_for ) - (w.points_against + l.points_against) AS plus_minus, 
                CAST(w.wins AS INT) AS wins, CAST(l.losses AS INT) AS losses FROM win_stats w JOIN loss_stats l ON w.WTeamID = l.LTeamID
                AND w.Season = l.Season)
                   
               
                
                SELECT s.*, w.wins  FROM 
                stat_table s JOIN tourney_wins w 
                ON w.WTeamID = s.Team AND w.Season = s.Season 
                WHERE s.Season >= 2003 
                ORDER BY s.Season, s.Team;
                
                """)
                
data = pd.DataFrame(np.array(cursor.fetchall()), 
                 columns=['Season', 'TeamID','FGPct','FG3Pct','FTPct','PFPG','PAPG','Plus/Minus','Wins','Losses','Tourney_wins' ])
                

print(data.shape)    

            
                
 
data.to_hdf("WnL_FG_FG3_etc.h5",str(1))


for x in data.columns[2:-1]:
    data[x] = (data[x]-np.mean(data[x]))/np.std(data[x])
    #plt.hist(y,100)
    #plt.show()
    
data.to_hdf("WnL_FG_FG3_etc_norm.h5",str(1))







               
                