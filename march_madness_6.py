#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 00:59:35 2019

@author: ianvaimberg
This file organizes offensive and deffensive quotient offensive speed and defensive speed (possesions per game)
SOS and off_eff have a moderate correlation to wins in the tournament 
"""

import pyodbc
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression 

a=pyodbc.connect('DRIVER=/Library/simba/sqlserverodbc/lib/libsqlserverodbc_sbu.dylib;'
                  'SERVER=localhost;'
                  'DATABASE=march_madness;'
                  'UID=sa;'
                  'PWD=Ivaim1997%')
cursor = a.cursor()

cursor.execute("""WITH wins_table AS (SELECT Season, WTeamID, COUNT(WTeamID) 
                AS wins FROM NCAATourneyDetailedResults_
                GROUP BY Season, WTeamID),

zero_wins AS (SELECT n.Season, n.TeamID AS WTeamID, 0 AS wins FROM NCAATourneySeeds n LEFT JOIN wins_table w
                ON w.Season = n.Season AND w.WTeamID = n.TeamID WHERE w.WTeamID IS NULL),

tourney_wins AS((SELECT * FROM wins_table)
UNION 
(SELECT * FROM zero_wins WHERE Season>=2003)),

 

             

 
win_stats AS (SELECT t.Season, t.WTeamID, SUM(r.WFGA)-SUM(r.WOR)+SUM(r.WTO)+(.4*SUM(r.WFTA)) AS off_Possesions, 
SUM(r.LFGA)-SUM(r.LOR)+SUM(r.LTO)+(.4*SUM(r.LFTA)) AS def_Possesions,
SUM(r.WScore) AS off_points, SUM(r.LScore) AS def_points, COUNT(r.WTeamID) AS wins
FROM RegularSeasonDetailedResults_ r RIGHT JOIN tourney_wins t ON r.Season = t.Season 
AND r.WTeamID = t.WTeamID  
GROUP BY t.Season, t.WTeamID), 
 
loss AS (SELECT t.Season, t.WTeamID AS LTeamID, SUM(r.LFGA)-SUM(r.LOR)+SUM(r.LTO)+(.4*SUM(r.LFTA)) AS off_Possesions,
SUM(r.WFGA)-SUM(r.WOR)+SUM(r.WTO)+(.4*SUM(r.WFTA)) AS def_Possesions, SUM(r.LScore) AS off_points,
SUM(r.WScore) AS def_points, COUNT(r.LTeamID) AS losses
FROM RegularSeasonDetailedResults_ r RIGHT JOIN tourney_wins t ON r.Season = t.Season 
AND r.LTeamID = t.WTeamID
GROUP BY t.Season, t.WTeamID),
         
loss_stats AS (SELECT Season, LTeamID, ISNULL(off_Possesions,0) AS off_Possesions, 
ISNULL(def_Possesions,0) AS def_Possesions, ISNULL(off_points, 0)AS off_points, 
ISNULL(def_points,0) AS def_points, ISNULL(losses,0) AS losses FROM loss),
  
stat_table AS (SELECT w.Season AS Season, w.WTeamID AS Team, (w.off_points+l.off_points)/(w.off_Possesions + l.off_Possesions) AS off_Eff, 
(w.off_Possesions + l.off_Possesions)/(w.wins+l.losses) AS off_speed,
(w.def_points+l.def_points)/(w.def_Possesions + l.def_Possesions) AS def_Eff,
(w.def_Possesions + l.def_Possesions)/(w.wins+l.losses) AS def_speed 
FROM win_stats w JOIN loss_stats l ON w.WTeamID = L.LTeamID AND w.Season = l.Season)
 
SELECT s.Season, s.Team, w.wins, s.off_Eff  , s.off_speed , 
s.def_Eff , s.def_speed 
FROM stat_table s JOIN tourney_wins w on s.Team = w.WTeamID AND s.Season = w.Season
WHERE s.Season >= 2003 
ORDER BY s.Season, s.Team;
 
""")               

results = np.array(cursor.fetchall())
results[:,3:] = np.round(results[:,3:].astype(float),3)

eff_data = pd.DataFrame(results, columns=['Season','Team','Tourney_wins','Off_eff','Off_speed','Def_eff','Def_speed'])
eff_data.to_hdf("Eff_data.h5",str(1))
#plt.subplot()
for x in ['Tourney_wins','Off_eff','Off_speed','Def_eff','Def_speed']:
    eff_data[x] = (eff_data[x]-np.mean(eff_data[x]))/np.std(eff_data[x])
    #plt.hist(y,100)
    #plt.show()
    
eff_data.to_hdf("Eff_data_norm.h5",str(1))

"""
tourney_sos = np.zeros(results.shape[0])
team_sos = pd.read_hdf("Exp_SOS.h5",str(1))

for i, row in enumerate(results): # this creates matching SOS from the teams and Season from results
    tourney_sos[i] = team_sos[(team_sos['Season'] == row[0]) & 
               (team_sos['Team'] == row[1])]['EXP_SOS_2']
#print(eff_data.sort_values(['Team','Season']),team_sos.sort_values(['Team','Season']))   
#print(team_sos.sort_values(['Team','Season']),team_sos.shape)
    
eff_data = eff_data.merge(team_sos , on=['Season','Team']).drop(columns='EXP_SOS_1')  
#print(eff_data.sort_values(['Team','Season']).drop(columns='EXP_SOS_1'))
eff_data.to_hdf("Eff&SOS.h5", str(1))  
"""  
"""   

wins = results[:,2].astype(int)
stat = (results[:,3]).astype(float).reshape(-1,1)

min_max_scaler = preprocessing.MinMaxScaler()
stat_scaled = min_max_scaler.fit_transform(stat)
new_stat = stat_scaled.flatten()

#print(new_stat.shape, tourney_sos.shape, wins.shape)
x = np.column_stack((new_stat,tourney_sos))

reg = LinearRegression().fit(new_stat.reshape(-1,1),wins)
r_2 = reg.score(new_stat.reshape(-1,1),wins)
print(r_2)
plt.scatter(wins,new_stat.reshape(-1,1))
"""

"""
ax = plt.figure().gca(projection='3d')
#ax = fig.add_subplot(111, projection='3d')
ax.scatter(new_stat, tourney_sos, wins)
ax.set_xlabel('Off_Eff')
ax.set_ylabel('SOS')
ax.set_zlabel('Wins')
"""
plt.show()




