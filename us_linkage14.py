# -*- coding: utf-8 -*-
"""
Created on Sat Aug  2 11:06:50 2025

@author: b60091cu
"""

import pandas as pd
import numpy as np
from edited_imputer import assign_weights
from index_functions import computing_measures

#A script to apply the estimation procedure to the Understanding Society wave 14 data

response = pd.read_csv(r"C:\Users\b60091cu\OneDrive - The University of Manchester\Desktop\n_indresp.tab",
                       sep='\t')
LSOA = pd.read_csv(r"C:\Users\b60091cu\OneDrive - The University of Manchester\Desktop\n_lsoa21_protect.tab",
                   sep='\t')
MSOA_LSOA_lookup = pd.read_csv(r"C:\Users\b60091cu\OneDrive - The University of Manchester\Lookup Files\MSOA_LSOA_lookup.csv")

#Linking from LSOAs to MSOAs
LSOA['LSOA21CD'] = LSOA['n_lsoa21'].str.replace('S','E')
MSOA = LSOA.merge(MSOA_LSOA_lookup[['LSOA21CD','MSOA21CD']], on='LSOA21CD', how='left').drop_duplicates()
MSOA_comp = MSOA.dropna()


#Joining from locations to responses
df = MSOA_comp.merge(response, on='n_hidp')
#Selecting necessary vars
variables = ['n_hidp', 'MSOA21CD', 'pidp', 'pid',
             'n_sex', 'n_dvage','n_howlng', 'n_fimnlabgrs_dv']
df = df[variables]
df.to_csv('us14df.csv')

#Joining to pre-computed neighbours, available in this repository
neighbours = pd.read_csv(r'C:/Users/b60091cu/OneDrive - The University of Manchester/Lookup Files/MSOA_neighbours_100.csv')

us14_dist = neighbours.merge(df, left_on='MSOA21CD_dest', right_on='MSOA21CD')

#Applying the estimation procedure to each indicator, see estimation_details

#Restricting to just employees
employees = us14_dist[us14_dist['n_fimnlabgrs_dv'] != 0]
#Income for women
women_emp = employees[employees['n_sex']==2]
men_emp = employees[employees['n_sex']==1]

imputed_inc_w = pd.DataFrame({'MSOA':[], 'Women':[]})
for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = women_emp[women_emp['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['n_fimnlabgrs_dv']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value, 'index':[0]})
    imputed_inc_w = pd.concat([imputed_inc_w, imputed_dict])

#Income for men
imputed_inc_m = pd.DataFrame({'MSOA':[], 'Men':[]})
for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = men_emp[men_emp['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['n_fimnlabgrs_dv']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Men':imputed_value, 'index':[0]})
    imputed_inc_m = pd.concat([imputed_inc_m, imputed_dict])

#Formatting and computing the indices    
imputed_inc = imputed_inc_w.merge(imputed_inc_m, on='MSOA')
computing_measures(imputed_inc, 'Women', 'Men', 'income')

#Low pay
#Getting national median pay
all_emp = response[response['n_fimnlabgrs_dv']!=0]
median_inc = all_emp['n_fimnlabgrs_dv'].median()

employees['not_low_pay'] = np.where(employees['n_fimnlabgrs_dv']>(2/3)*median_inc, 1, 0)

#Women
women_emp = employees[employees['n_sex']==2]
women_emp.to_csv('women_emp.csv')
imputed_lp_w = pd.DataFrame({'MSOA':[], 'Women':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = women_emp[women_emp['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['not_low_pay']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value, 'index':[0]})
    imputed_lp_w = pd.concat([imputed_lp_w, imputed_dict])
    
#Men
men_emp = employees[employees['n_sex']==1]
imputed_lp_m = pd.DataFrame({'MSOA':[], 'Men':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = men_emp[men_emp['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['not_low_pay']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Men':imputed_value, 'index':[0]})
    imputed_lp_m = pd.concat([imputed_lp_m, imputed_dict])

imputed_lp = imputed_lp_w.merge(imputed_lp_m, on='MSOA')
computing_measures(imputed_lp, 'Women', 'Men', 'not_low_pay')

#Domestic labour
us14_dist['n_howlng'] = us14_dist['n_howlng'].replace(to_replace=[-7,-2,-1,-9], value=np.nan)
#Women
women_dl = us14_dist[us14_dist['n_sex']==2]
imputed_dl_w = pd.DataFrame({'MSOA':[], 'Women':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = women_dl[women_dl['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std() 
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['n_howlng']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value, 'index':[0]})
    imputed_dl_w = pd.concat([imputed_dl_w, imputed_dict])

#Men
men_dl = us14_dist[us14_dist['n_sex']==1]
imputed_dl_m = pd.DataFrame({'MSOA':[], 'Men':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = men_dl[men_dl['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['n_howlng']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Men':imputed_value, 'index':[0]})
    imputed_dl_m = pd.concat([imputed_dl_m, imputed_dict])

imputed_dl = imputed_dl_w.merge(imputed_dl_m, on='MSOA')
computing_measures(imputed_dl, 'Women', 'Men', 'dom_lab')

#Exporting final results
imputed_inc.to_csv('inc_computed.csv')
imputed_lp.to_csv('lp_computed.csv')
imputed_dl.to_csv('dl_computed.csv')

