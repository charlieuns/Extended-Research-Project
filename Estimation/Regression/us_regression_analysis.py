# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 17:45:57 2025

@author: b60091cu
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

#A script to explore the spatial variations in correlations between MSOAs
#See also: edu_regression_analysis

MSOA_dist = pd.read_csv("MSOA_dist.csv")
us14df = pd.read_csv('us14df.csv')

#Filtering the full dataset to just employees and averaging to MSOA
employees = us14df[us14df['n_fimnlabgrs_dv'] != 0]
emp_avg = employees.groupby('MSOA21CD')['n_fimnlabgrs_dv'].mean()

#Joining to distances on both sides and computing difference in means
emp_dist = MSOA_dist.merge(emp_avg, left_on='MSOA21CD_origin', right_index=True)
emp_dist.rename(columns={'n_fimnlabgrs_dv':'origin_inc'}, inplace=True)
emp_dist = emp_dist.merge(emp_avg, left_on='MSOA21CD_dest', right_index=True)
emp_dist.rename(columns={'n_fimnlabgrs_dv':'dest_inc'}, inplace=True)
emp_dist['diff'] = np.abs(emp_dist['dest_inc']-emp_dist['origin_inc'])

emp_comp = emp_dist.dropna(subset=['dist','same_LA'])

#Multiple linear regression of difference on distance and same_LA status
y = emp_comp['diff'].to_numpy()
X = np.array(emp_comp[['dist','same_LA']], dtype=float).reshape(-1,2)

emp_distance_mod = sm.OLS(y,X)
emp_distance_reg = emp_distance_mod.fit()

#Saving the results, see the Appendix to the report
print(emp_distance_reg.summary())
emp_distance_reg.save('emp_reg.pickle')

