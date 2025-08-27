# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 12:25:42 2025

@author: b60091cu
"""

import pandas as pd
import numpy as np
from edited_imputer import assign_weights

#A script to conduct a sensitivity analysis of the estimation procedure in the not low pay indicator

neighbours = pd.read_csv('MSOA_neighbours_100.csv')
women_emp = pd.read_csv('women_emp.csv')
MSOA_GM_only = pd.read_csv('GM_LA_MSOA_lookup.csv')

#Setting a grid of values for k between 0 and 5
param_grid = list(np.linspace(0,5, num=11))

#Iterating over the parameter grid
variances = pd.DataFrame({'Constant':[],'Variance':[]})
for const in param_grid:

    imputed_lp_w = pd.DataFrame({'MSOA':[], 'Women':[]})
    
    #Conducting the estimation procedure for that value of k, see estimation_details
    for i in neighbours['MSOA21CD_origin'].unique():
        subset_i = women_emp[women_emp['MSOA21CD_origin']==i]
        sd = subset_i['dist'].std() * const
        subset_weighted = assign_weights(subset_i, sd, 0.9)
        imputed_value = (subset_weighted['norm_weight']*subset_weighted['not_low_pay']).sum()
        imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value, 'index':[0]})
        imputed_lp_w = pd.concat([imputed_lp_w, imputed_dict])

    #Aggregating the result to LAD level so it's comparable with GEIUK    
    imputed_lp_w['w_lp'] = imputed_lp_w['Women'] / imputed_lp_w['Women'].mean()
    imputed_lp_w_join = imputed_lp_w.merge(MSOA_GM_only, left_on='MSOA', right_on='MSOA21CD')      
    imputed_lp_w_LA = imputed_lp_w_join.groupby('LAD22NM')['w_lp'].mean()
    
    #Computing and storing the variance
    var = imputed_lp_w_LA.var()
    var_const_dict = pd.DataFrame({'Constant':const, 'Variance':var}, index=[0])
    variances = pd.concat([variances, var_const_dict])
    
#Not low pay variance for women is approximately 0.017 so again 1 seems an appropriate choice
#Export variances to csv
variances.to_csv('us_grid_search.csv')

