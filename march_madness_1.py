# -*- coding: utf-8 -*-
"""
Spyder Editor

This file created Weekly_SOS table that has average ranking of each team for each week since 2003.
"""

import pyodbc
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
import h5py
import time  

start = time.time()
a=pyodbc.connect('DRIVER=/Library/simba/sqlserverodbc/lib/libsqlserverodbc_sbu.dylib;'
                  'SERVER=localhost;'
                  'DATABASE=march_madness;'
                  'UID=sa;'
                  'PWD=Ivaim1997%')
                  
cursor = a.cursor()


col_list = ['Season', 'Team']
for i in range(19):
    col_list.append('Week_'+str(i+1))

weekly_SOS = pd.DataFrame(columns=col_list)


week_start = np.array([7*x for x in range(19)])
week_end = np.array([6+(7*x) for x in range(19)])
years = np.array([2003+i  for i in range(17)])

for start, end in zip(week_start, week_end):
    print(start)
    cursor.execute("""SELECT n.Season, n.Team, AVG(m.OrdinalRank) FROM 
                   (SELECT * FROM MasseyOrdinals_thru_2019_day_128_ WHERE Season >= 2003 ) AS m 
                   RIGHT JOIN (SELECT DISTINCT Season, Team FROM ( SELECT Season, WTeamID AS Team FROM 
                   RegularSeasonCompactResults UNION 
                   SELECT Season, LTeamID AS Team FROM RegularSeasonCompactResults ) AS r
                    WHERE r.Season >=  2003 ) AS n ON
                    m.Season = n.Season AND m.TeamID = n.Team
                   AND m.RankingDayNum BETWEEN """+str(start)+""" AND """+str(end)+"""
                   GROUP BY n.Team, n.Season
                   ORDER BY n.Season, n.Team; """)

    results = np.array(cursor.fetchall())
    #print(results.shape)
    #break
    if(start == 0):
        weekly_SOS['Season'] = results[:,0]
        weekly_SOS['Team'] = results[:,1]
        
    
    weekly_SOS['Week_'+str(int((start/7)+1))] = results[:,2] #converts start to week number 

weekly_SOS.to_hdf("Weekly_SOS.h5",str(1))   

print(weekly_SOS) 
      




