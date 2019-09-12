ar#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 15:42:15 2019

@author: ianvaimberg
This file aggregates every teams schedule since 2003 and says which week a game takes place
"""



import pyodbc
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
for i in range(40):
    col_list.append('Game '+str(i+1))

cols = ['Season', 'Team']
for i in range(134):
    cols.append('Day '+str(i))

master_schedule = pd.DataFrame(columns=cols, dtype=np.int64)
   
years = np.array([2003+i  for i in range(17)])    


cursor.execute("""SELECT DISTINCT TeamID FROM NCAATourneySeeds
                   ORDER BY TeamID""")
teams = np.array(cursor.fetchall())
    
for team in teams:
    print(team[0])
    cursor.execute("""WITH first_half AS (SELECT WTeamID, LTeamID, DayNum, Season FROM 
                   RegularSeasonCompactResults WHERE WTeamID = """+str(team[0])+""" 
                   AND Season >= 2003 ), 
    
                    second_half AS (SELECT LTeamID, WTeamID, DayNum, Season FROM 
                    RegularSeasonCompactResults WHERE LTeamID = """+str(team[0])+""" 
                    AND Season >= 2003)
                    
                    SELECT * FROM first_half
                    UNION 
                    SELECT * FROM second_half
                    ORDER BY Season, DayNum; """)
                    
    temp = np.array(cursor.fetchall())
    years = np.unique(temp[:,3])
    one_team = pd.DataFrame(columns = cols, dtype=np.int64)
    one_team['Season'] = years; 
    one_team['Team'] = team[0]; #one_team data frame with year and Team tabled rows
    min_year = min(years)
    for dp in temp:
        
        one_team.at[dp[3]-min_year,'Day '+str(dp[2])] = dp[1] #placing in matchup data at in temp table 
    
    
    master_schedule = master_schedule.append(one_team)
   
master_schedule.to_hdf('Team_schedules.h5',str(1)) #this file contains every teams schedule 
        
    
    
                  
    
    
    
  
       
                
    
    
