#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 15:40:23 2019

@author: ianvaimberg
This file creates the last day rank h5 file 
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



cursor.execute("""WITH last_day_rank AS (SELECT TeamID, AVG(OrdinalRank) AS Estimated_rank, 
                                    Season FROM MasseyOrdinals_thru_2019_day_128_
                                    WHERE RankingDayNum=128
                                    GROUP BY Season, TeamID),
                                   
                                    wins_table AS (SELECT Season, WTeamID, COUNT(WTeamID) 
                                    AS wins FROM NCAATourneyDetailedResults_
                                    GROUP BY Season, WTeamID),

                                    no_wins AS (SELECT n.Season, n.TeamID AS WTeamID, 0 AS wins 
                                    FROM NCAATourneySeeds n LEFT JOIN wins_table w
                                    ON w.Season = n.Season AND w.WTeamID = n.TeamID WHERE w.WTeamID IS NULL),
                
                                    tourney_wins AS ((SELECT * FROM wins_table) UNION (SELECT * FROM no_wins)) 

                                    SELECT l.* FROM last_day_rank l JOIN tourney_wins t ON l.Season = t.Season
                                    AND l.TeamID = t.WTeamID
                                    ORDER BY l.Season, l.TeamID;
                                    """)
data = pd.DataFrame(np.array(cursor.fetchall()),columns=['TeamID','Rank_day_129','Season'])

data.to_hdf("Last_day_rank.h5",str(1))