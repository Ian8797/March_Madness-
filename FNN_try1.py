#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 14:19:52 2019

@author: ianvaimberg

Pretty good accuracy toping out at around 73% 
"""
import pandas as pd
import pyodbc
import numpy as np
from sklearn.preprocessing import StandardScaler
import random
import tensorflow as tf

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
drop_cols = ['Season','WTeamID','Win_Seed','LTeamID','Lose_Seed']
imp_data = results.drop(columns=drop_cols)
#print(imp_data['SOS_diff'])
target = np.zeros((imp_data.shape[0],2))

for x in range(target.shape[0]):   #all target vectors are [1,0] (winner-loser) or [0,1] (loser-winner)
    target[x,0] = random.choice([1,0]) # will really need to play attention to order when inserting 2019 data
    target[x,1] = 1-target[x,0]

for x,i in zip(range(imp_data.shape[0]), target[:,0]):
    if i == 0:
        imp_data.iloc[x] = imp_data.iloc[x]*-1 #multipled some by -1 to show (loser-winner)
        
       
data_std = StandardScaler().fit_transform(imp_data)

data_std = pd.DataFrame(data_std)
data_std["T1"] = target[:,0]
data_std["T2"] = target[:,1]

shuffled = tf.random.shuffle(data_std.values)

k = 5 # the k in k_fold
ind = [int(int(shuffled.shape[0])/k)*x for x in range(k)]
ind.append(shuffled.shape[0])

full_index = np.arange(0,1048)
results = []

data_std = tf.slice(shuffled,[0,0],[-1,16]) #data slice
target = tf.slice(shuffled,[0,16],[-1,2]) # target slice
#print(target)     
for x in range(k):
    
   
    model = tf.keras.models.Sequential()
    
   
    
    model.add(tf.keras.layers.Dense(8, input_dim=imp_data.shape[1], activation='relu'))
    model.add(tf.keras.layers.Dense(2,activation='sigmoid'))
    
    model.compile(loss='mean_squared_error',optimizer='adam',metrics=['binary_accuracy'])
    
    # working on k - fold cross validation, 5 fold 
    train_indices = np.delete(full_index,np.s_[ind[x]:ind[x+1]])
    test_indices = np.delete(full_index,train_indices)
    #print(train_indices,test_indices)
 
    
    history = model.fit(tf.gather(data_std,tf.constant(train_indices)),
                        tf.gather(target,tf.constant(train_indices)), 
                        epochs=200, steps_per_epoch=1, verbose=1)
    test_data = np.array(tf.gather(data_std,tf.constant(test_indices)))
    prediction = model.predict(test_data)
    
    b = np.zeros_like(prediction)
    b[np.arange(len(prediction)), prediction.argmax(1)] = 1
    length = len(test_indices) 
    compare = tf.gather(target,test_indices).numpy()
    #print(b,type(b),compare,type(compare))
    #break
    results.append((sum(b == compare/length)[0]))
    


print(results)















