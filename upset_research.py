#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 23:12:05 2019

@author: ianvaimberg
Investigating relationships between upsets 
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

cursor.execute("""WITH win_seed AS(SELECT r.Season, r.DayNum, CAST(SUBSTRING(s.seed,2,2) AS INT) AS Seed, 
r.WTeamID, r.WScore, r.LTeamID FROM NCAATourneyCompactResults_ r JOIN NCAATourneySeeds s 
ON r.Season=s.Season AND r.WTeamID = s.TeamID 
WHERE r.Season >= 2003),

loss_seed AS(SELECT r.Season, r.DayNum, CAST(SUBSTRING(s.seed,2,2) AS INT) AS Seed, 
r.LTeamID, r.LScore, r.WTeamID FROM NCAATourneyCompactResults_ r JOIN NCAATourneySeeds s 
ON r.Season=s.Season AND r.LTeamID = s.TeamID 
WHERE r.Season >= 2003),
 
seed_table AS( SELECT w.Season, w.DayNum, w.Seed AS WSeed, w.WTeamID, w.WScore, l.Seed AS LSeed, l.LTeamID, l.LScore 
FROM loss_seed l JOIN win_seed w ON w.DayNum=l.DayNum AND w.Season = l.Season AND w.LTeamID=l.LTeamID
WHERE w.Seed > l.Seed ), 
/*This creates seed table with info on game score only for tournament upsets */ 

last_day_rank AS (SELECT TeamID, AVG(OrdinalRank) AS Estimated_rank, Season FROM MasseyOrdinals_thru_2019_day_128_
WHERE RankingDayNum=128
GROUP BY Season, TeamID),

tourney_rank AS (SELECT season, CAST(SUBSTRING(seed,2,2) AS INT)*4 AS Approx_rank, TeamID FROM NCAATourneySeeds
WHERE Season >= 2003),

seed_compare AS (SELECT l.Season, L.TeamID, l.Estimated_rank, t.Approx_rank, t.Approx_rank/4 AS Seed FROM tourney_rank t JOIN last_day_rank l 
ON t.Season = l.Season AND t.TeamID = l.TeamID 
WHERE l.Estimated_rank + 10 <= t.Approx_rank)


SELECT t.Season, t.DayNum, t.WSeed, c1.Approx_rank, c1.Estimated_rank, t.WTeamID, t.LSeed, 
t.LSeed*4 AS Approx_rank, c2.Estimated_rank, t.LTeamID, c1.Approx_rank - t.LSeed*4 AS Exp_diff,
c1.Estimated_rank - c2.Estimated_rank AS Diff_Est_rank
FROM Seed_table t 
JOIN seed_compare c1 ON c1.TeamID = t.WTeamID AND c1.Season = t.Season 
JOIN last_day_rank c2 ON c2.TeamID = t.LTeamID AND c2.Season = t.Season
ORDER BY Diff_Est_rank; 
""")

upsets = np.array(cursor.fetchall())

cursor.execute("""WITH win_seed AS(SELECT r.Season, r.DayNum, CAST(SUBSTRING(s.seed,2,2) AS INT) AS Seed, 
r.WTeamID, r.WScore, r.LTeamID FROM NCAATourneyCompactResults_ r JOIN NCAATourneySeeds s 
ON r.Season=s.Season AND r.WTeamID = s.TeamID 
WHERE r.Season >= 2003),

loss_seed AS(SELECT r.Season, r.DayNum, CAST(SUBSTRING(s.seed,2,2) AS INT) AS Seed, 
r.LTeamID, r.LScore, r.WTeamID FROM NCAATourneyCompactResults_ r JOIN NCAATourneySeeds s 
ON r.Season=s.Season AND r.LTeamID = s.TeamID 
WHERE r.Season >= 2003),
 
seed_table AS( SELECT w.Season, w.DayNum, w.Seed AS WSeed, w.WTeamID, w.WScore, l.Seed AS LSeed, l.LTeamID, l.LScore 
FROM loss_seed l JOIN win_seed w ON w.DayNum=l.DayNum AND w.Season = l.Season AND w.LTeamID=l.LTeamID
WHERE w.Seed <= l.Seed ), 
 

last_day_rank AS (SELECT TeamID, AVG(OrdinalRank) AS Estimated_rank, Season FROM MasseyOrdinals_thru_2019_day_128_
WHERE RankingDayNum=128
GROUP BY Season, TeamID),

tourney_rank AS (SELECT season, CAST(SUBSTRING(seed,2,2) AS INT)*4 AS Approx_rank, TeamID FROM NCAATourneySeeds
WHERE Season >= 2003),

seed_compare AS (SELECT l.Season, L.TeamID, l.Estimated_rank, t.Approx_rank, t.Approx_rank/4 AS Seed FROM tourney_rank t JOIN last_day_rank l 
ON t.Season = l.Season AND t.TeamID = l.TeamID)


SELECT t.Season, t.DayNum, t.WSeed, c1.Approx_rank, c1.Estimated_rank, t.WTeamID, t.LSeed, 
t.LSeed*4 AS Approx_rank, c2.Estimated_rank, t.LTeamID, t.LSeed*4 - c1.Approx_rank AS Exp_diff,
c2.Estimated_rank - c1.Estimated_rank AS Diff_Est_rank
FROM Seed_table t 
JOIN seed_compare c1 ON c1.TeamID = t.WTeamID AND c1.Season = t.Season 
JOIN last_day_rank c2 ON c2.TeamID = t.LTeamID AND c2.Season = t.Season
ORDER BY Diff_Est_rank; """)

non_upsets = np.array(cursor.fetchall())

cursor.execute(""" WITH win_seed AS(SELECT r.Season, r.DayNum, CAST(SUBSTRING(s.seed,2,2) AS INT) AS Seed, 
r.WTeamID, r.WScore, r.LTeamID FROM NCAATourneyCompactResults_ r JOIN NCAATourneySeeds s 
ON r.Season=s.Season AND r.WTeamID = s.TeamID 
WHERE r.Season >= 2003),

loss_seed AS(SELECT r.Season, r.DayNum, CAST(SUBSTRING(s.seed,2,2) AS INT) AS Seed, 
r.LTeamID, r.LScore, r.WTeamID FROM NCAATourneyCompactResults_ r JOIN NCAATourneySeeds s 
ON r.Season=s.Season AND r.LTeamID = s.TeamID 
WHERE r.Season >= 2003),
 
seed_table AS( SELECT w.Season, w.DayNum, w.Seed AS WSeed, w.WTeamID, w.WScore, l.Seed AS LSeed, l.LTeamID, l.LScore 
FROM loss_seed l JOIN win_seed w ON w.DayNum=l.DayNum AND w.Season = l.Season AND w.LTeamID=l.LTeamID ), 
 

last_day_rank AS (SELECT TeamID, AVG(OrdinalRank) AS Estimated_rank, Season FROM MasseyOrdinals_thru_2019_day_128_
WHERE RankingDayNum=128
GROUP BY Season, TeamID),

tourney_rank AS (SELECT season, CAST(SUBSTRING(seed,2,2) AS INT)*4 AS Approx_rank, TeamID FROM NCAATourneySeeds
WHERE Season >= 2003),

seed_compare AS (SELECT l.Season, L.TeamID, l.Estimated_rank, t.Approx_rank, t.Approx_rank/4 AS Seed FROM tourney_rank t JOIN last_day_rank l 
ON t.Season = l.Season AND t.TeamID = l.TeamID)
/*WHERE ABS(Estimated_rank - Approx_rank) >= 10 )*/

SELECT t.Season, t.DayNum, t.WSeed, c1.Estimated_rank, t.WTeamID, t.LSeed, 
t.LSeed*4 AS Approx_rank, c2.Estimated_rank, t.LTeamID
 
FROM Seed_table t 
JOIN seed_compare c1 ON c1.TeamID = t.WTeamID AND c1.Season = t.Season 
JOIN last_day_rank c2 ON c2.TeamID = t.LTeamID AND c2.Season = t.Season;""")

rank_regress =np.array(cursor.fetchall())






"""

#plt.figure(figsize=(20,10))

plt.scatter(upsets[:,10],upsets[:,11],color='r')
plt.scatter(non_upsets[:,10],non_upsets[:,11], color='k')

plt.xlabel("Exp_diff From Seeds")
plt.ylabel("Diff from Massy Rank")

plt.show()

"""

