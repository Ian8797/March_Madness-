#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 16:01:29 2019

@author: ianvaimberg

This file creates the normalized SOS statistic, I made 2 
different versions but EXP_SOS_2 is the best
"""
import pandas as pd
from sklearn import preprocessing 
import numpy as np 
import matplotlib.pyplot as plt

raw_SOS = pd.read_hdf("raw_SOS.h5",str(1))
exclude = ['Season', 'Team']
temp_raw_SOS = raw_SOS.drop(exclude, axis=1)
sos = temp_raw_SOS.agg(np.mean, axis=1).values

team_sos = pd.DataFrame({'Season': raw_SOS['Season'], 'Team' : raw_SOS['Team'],
                         'SOS': sos })

stand_sos = ((sos-np.mean(sos))/np.std(sos))



plt.hist(stand_sos, 100)
plt.show()




team_sos = pd.DataFrame({'Season': raw_SOS['Season'], 'Team' : raw_SOS['Team'],
                         'Centered_SOS': stand_sos })

team_sos.to_hdf('SOS.h5',str(1))



