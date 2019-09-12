#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:20:29 2019

@author: ianvaimberg

This file will finish calculating SOS for each team since 2003 
"""


import h5py
import pandas as pd

def get_rank(ranking, sos_season, val, week_num):
    
    while((week_num<20)):
        rank = ranking[(ranking['Season'] == sos_season) & (ranking['Team'] == val)]['Week_'+str(week_num)]
        week_num +=1
        if( rank.values != None):
            #print(rank.values[0])
            return rank.values[0] 
    

    


schedules = pd.read_hdf("Team_schedules.h5",str(1)).reset_index(drop=True)
ranking = pd.read_hdf("Weekly_SOS.h5" , str(1)).reset_index(drop=True)

cols = ['Season', 'Team']
for i in range(133):
    cols.append('Day '+str(i))

raw_SOS = pd.DataFrame(columns= cols).reset_index(drop=True)
raw_SOS['Season'] = schedules['Season']
raw_SOS['Team'] = schedules['Team']
#print(schedules)

for index, row in schedules.iterrows():
    print(index)
    
    for i, val in enumerate(row[2:]):
        if val >= 0 :
            
            sos_season = schedules.iloc[index]['Season'] #needed season
            week_num = int((i/7) + 1) #needed week 
            #print(val, week_num, sos_season)
            rank = get_rank(ranking, sos_season, val, week_num)
            
            raw_SOS.at[index, cols[i+2]] = rank
    #print(raw_SOS)       
           #line above inserts weekly_SOS into the table RAw_SOS table
            
raw_SOS.to_hdf('raw_SOS.h5',str(1))    #will contain aveage ranking where data wasnt available 
    
          
