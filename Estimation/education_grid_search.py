#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 17:09:26 2025

@author: charlieunsworth
"""

import pandas as pd
import numpy as np
from edited_imputer import assign_weights

#A script to conduct a sensitivity analysis of the estimation procedure in the Education domain

neighbours = pd.read_csv('MSOA_neighbours_50.csv')
girls_dist = pd.read_csv('girls_dist.csv')
MSOA_GM_only = pd.read_csv('GM_LA_MSOA_lookup.csv')

#Setting a grid of values for k between 0 and 5
param_grid = list(np.linspace(0,5, num=11))

#Iterating over the parameter grid
variances = pd.DataFrame({'Constant':[],'Variance':[]})
for const in param_grid:

    #Conducting the estimation procedure for that value of k, see estimation_details
    imputed_girls = pd.DataFrame({'MSOA':[], 'Women':[]})
    for i in neighbours['MSOA21CD_origin'].unique():
            subset_i = girls_dist[girls_dist['MSOA21CD_origin']==i]
            sd = subset_i['dist'].std() * const
            subset_weighted = assign_weights(subset_i, sd, 0.9)
            imputed_value = (subset_weighted['norm_weight']*subset_weighted['passed_basics']).sum()
            imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value}, index=[0])
            imputed_girls = pd.concat([imputed_girls, imputed_dict])

    #Aggregating the result to LAD level so it's comparable with GEIUK
    imputed_girls['w_gcses'] = imputed_girls['Women'] / imputed_girls['Women'].mean()
    imputed_girls_join = imputed_girls.merge(MSOA_GM_only, left_on='MSOA', right_on='MSOA21CD')      
    imputed_girls_LA = imputed_girls_join.groupby('LAD22NM')['w_gcses'].mean()
    
    #Computing and storing the variance
    var = imputed_girls_LA.var()
    var_const_dict = pd.DataFrame({'Constant':const, 'Variance':var}, index=[0])
    variances = pd.concat([variances, var_const_dict])

#Whole domain variance for education_w is 0.018, so a constant of 1 is an appropriate choice
variances.to_csv('edu_grid_search.csv')
