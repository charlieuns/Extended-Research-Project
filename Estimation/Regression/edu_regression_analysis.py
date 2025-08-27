#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 11:06:23 2025

@author: charlieunsworth
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import csv

#A script to explore the spatial variation in correlations between MSOA values

distances = pd.read_csv('MSOA_distances.csv')
MSOA_lookup = pd.read_csv('MSOA_lookup.csv')
girls = pd.read_csv('girls_df.csv')
boys = pd.read_csv('boys_df.csv')

#Generating a new csv with both distance and same_LA attributes, available in the repository
MSOA_LA = distances.merge(MSOA_lookup, left_on='MSOA21CD_origin', right_on='MSOA21CD')
MSOA_LA.rename(columns={'LAD22CD': 'LA_origin'}, inplace=True)
MSOA_LA = MSOA_LA.merge(MSOA_lookup, left_on='MSOA21CD_dest', right_on='MSOA21CD')
MSOA_LA.rename(columns={'LAD22CD': 'LA_dest'}, inplace=True)

MSOA_LA['same_LA'] = pd.to_numeric(MSOA_LA['LA_origin'] == MSOA_LA['LA_dest'])
MSOA_dist = MSOA_LA[['MSOA21CD_origin', 'MSOA21CD_dest', 'dist', 'same_LA']]
MSOA_dist.to_csv('MSOA_dist.csv')

#Averaging the raw values to MSOA level
girls_avg = girls.groupby('MSOA')['passed_basics'].mean()
boys_avg = boys.groupby('MSOA')['passed_basics'].mean()

#Joining to the distances on both sides
girls_dist = MSOA_dist.merge(girls_avg, left_on='MSOA21CD_origin', right_index=True)
girls_dist.rename(columns={'passed_basics':'origin_passed'}, inplace=True)
girls_dist = girls_dist.merge(girls_avg, left_on='MSOA21CD_dest', right_index=True)
girls_dist.rename(columns={'passed_basics':'dest_passed'}, inplace=True)
girls_dist['diff'] = np.abs(girls_dist['dest_passed']-girls_dist['origin_passed'])

boys_dist = MSOA_dist.merge(boys_avg, left_on='MSOA21CD_origin', right_index=True)
boys_dist.rename(columns={'passed_basics':'origin_passed'}, inplace=True)
boys_dist = boys_dist.merge(girls_avg, left_on='MSOA21CD_dest', right_index=True)
boys_dist.rename(columns={'passed_basics':'dest_passed'}, inplace=True)
boys_dist['diff'] = np.abs(boys_dist['dest_passed']-boys_dist['origin_passed'])

#Subsetting to a complete case analysis
girls_dist_comp = girls_dist.dropna(subset=['dist','same_LA'])
boys_dist_comp = boys_dist.dropna(subset=['dist','same_LA'])

#Conducting a multiple linear regression of difference on distance and same_LA status
#Girls
y = girls_dist_comp['diff'].to_numpy()
X = np.array(girls_dist_comp[['dist','same_LA']], dtype=float).reshape(-1,2)

girls_distance_mod = sm.OLS(y,X)
girls_distance_reg = girls_distance_mod.fit()
print(girls_distance_reg.summary())

#Boys
y = boys_dist_comp['diff'].to_numpy()
X = np.array(boys_dist_comp[['dist','same_LA']], dtype=float).reshape(-1,2)

boys_distance_mod = sm.OLS(y,X)
boys_distance_reg = boys_distance_mod.fit()
print(boys_distance_reg.summary())

#Exporting those results, see the Appendix to the report
girls_summary = girls_distance_reg.summary().as_csv()
girls_file = open("girls_summary.csv",'w')
girls_file.write(girls_summary)
girls_file.close()

boys_summary = boys_distance_reg.summary().as_csv()
boys_file = open("boys_summary.csv",'w')
boys_file.write(boys_summary)
boys_file.close()



