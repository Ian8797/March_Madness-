#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 19:30:38 2019

@author: ianvaimberg
Basic trend research pertaining to the last 10 games of the season: Specifically plus mimus and wins in last 10 
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


cursor.execute("""WITH wins_table AS (SELECT Season, WTeamID, COUNT(WTeamID) 
                AS wins FROM NCAATourneyDetailedResults_
                GROUP BY Season, WTeamID), 

no_wins AS (SELECT n.Season, n.TeamID AS WTeamID, 0 wins FROM NCAATourneySeeds n LEFT JOIN wins_table w
ON w.Season = n.Season AND w.WTeamID = n.TeamID WHERE w.WTeamID IS NULL),

tourney_wins AS ((SELECT * FROM wins_table) UNION (SELECT * FROM no_wins))

SELECT * FROM tourney_wins
WHERE Season >= 2003 
ORDER BY Season,WTeamID""")

wins_data = np.array(cursor.fetchall())

wins_last10_data = np.zeros((wins_data.shape[0],5))

wins_last10_data[:,0] = wins_data[:,0]  #tranfers Season to final array in (ORDER BY Season, TeamID) form 
wins_last10_data[:,1] = wins_data[:,1]  #tranfers TeamID to final array in (ORDER BY Season, TeamID) form
wins_last10_data[:,2] = wins_data[:,2]  #tranfers win data to final array in (ORDER BY Season, TeamID) form

wins = pd.DataFrame(wins_data)

seasons = np.array([2003+x for x in range(17)])
counter = 0

for s in seasons: 
    print(s)
    teams = wins.loc[wins[0] == s][1].values
    for t in teams:
        
        cursor.execute("""WITH wins AS (SELECT 1 AS WoL, Season, DayNum, WTeamID AS Team1, LTeamID AS Team2, 
        WScore AS Score1, LScore AS Score2 FROM RegularSeasonCompactResults),
        
        losses AS (SELECT 0 AS WoL, Season, DayNum, LTeamID AS Team1, WTeamID AS Team2, 
        LScore AS Score1, WScore AS Score2 FROM RegularSeasonCompactResults),
        
        games AS ((SELECT * FROM wins) UNION (select * FROM losses))
        
        
        SELECT SUM(WoL)  , SUM(Score1) - SUM(Score2) FROM (SELECT TOP 10 * FROM games WHERE Season = """+str(s)+""" 
        AND (Team1 = """+str(t)+""") 
        ORDER BY DayNum DESC) AS T""")
        #print(np.array(cursor.fetchall())[0])
        wins_last10_data[counter,3:] = np.array(cursor.fetchall())
        counter+=1
        
last10 = pd.DataFrame(wins_last10_data, columns=["Season", "TeamID", "Tourney_wins","Winslast10","Plus/Minus Last Ten"])

last10.to_hdf("Last10info.h5",str(1))      
        
        
"""   
plt.scatter(wins_last10_data[:,0], wins_last10_data[:,1])
fit = np.polyfit(wins_last10_data[:,0], wins_last10_data[:,1] , 1)
fit_fn = np.poly1d(fit)
plt.plot(wins_last10_data[:,0], fit_fn(wins_last10_data[:,0]), '--o')
plt.xlabel("wins")
plt.ylabel("wins last 10")
plt.show()

plt.scatter(wins_last10_data[:,0], wins_last10_data[:,2])
plt.xlabel("wins")
plt.ylabel("plus minus last 10 ")
plt.show()
"""
        
