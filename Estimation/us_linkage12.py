# -*- coding: utf-8 -*-
"""
Created on Sat Aug  2 13:49:29 2025

@author: b60091cu
"""

import pandas as pd
import numpy as np
from index_functions import computing_measures

#A script to apply the estimation procedure to the Understanding Society wave 12 data


response = pd.read_csv(r"C:\Users\b60091cu\OneDrive - The University of Manchester\Desktop\l_indresp.tab",
                       sep='\t')
LSOA = pd.read_csv(r"C:\Users\b60091cu\OneDrive - The University of Manchester\Desktop\l_lsoa21_protect.tab",
                   sep='\t')
MSOA_LSOA_lookup = pd.read_csv(r"C:\Users\b60091cu\OneDrive - The University of Manchester\Lookup Files\MSOA_LSOA_lookup.csv")

#Linking from LSOAs to MSOAs
LSOA['LSOA21CD'] = LSOA['l_lsoa21'].str.replace('S','E')
MSOA = LSOA.merge(MSOA_LSOA_lookup[['LSOA21CD','MSOA21CD']], on='LSOA21CD', how='left').drop_duplicates()
MSOA_comp = MSOA.dropna()


#Joining from locations to responses
df = MSOA_comp.merge(response, on='l_hidp')

#Selecting necessary vars
pp_vars = ['l_hidp', 'MSOA21CD', 'pidp', 'pid',
             'l_sex', 'l_dvage', 'l_vote7',
             'l_orgmt96', 'l_orgmcawi96']
pp_df = df[pp_vars]

#Combining the participation responses
pp_df[['l_orgmt96', 'l_orgmcawi96']] = pp_df[['l_orgmt96', 'l_orgmcawi96']].replace(to_replace=[-8,-7,-2,-1], value=0)
pp_df['not_part'] =  pp_df['l_orgmt96'] + pp_df['l_orgmcawi96']
pp_df['part'] =1-pp_df['not_part']
#Recoding voting responses
pp_df['l_vote7'] = pp_df['l_vote7'].replace(to_replace=2, value=0)
pp_df['l_vote7'] = pp_df['l_vote7'].replace(to_replace=[-8,-7,-2,-1,3,-9], value=np.nan)


#Joining to pre-computed neighbours
neighbours = pd.read_csv(r'C:/Users/b60091cu/OneDrive - The University of Manchester/Lookup Files/MSOA_neighbours_100.csv')

us12_dist = neighbours.merge(pp_df, left_on='MSOA21CD_dest', right_on='MSOA21CD')

#Participation for women
from edited_imputer import assign_weights

women = us12_dist[us12_dist['l_sex']==2]
imputed_part_w = pd.DataFrame({'MSOA':[], 'Women':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = women[women['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['part']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value, 'index':[0]})
    imputed_part_w = pd.concat([imputed_part_w, imputed_dict])
   

#Participation for men
men = us12_dist[us12_dist['l_sex']==1]
imputed_part_m = pd.DataFrame({'MSOA':[], 'Men':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = men[men['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['part']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Men':imputed_value, 'index':[0]})
    imputed_part_m = pd.concat([imputed_part_m, imputed_dict])
    
imputed_part = imputed_part_w.merge(imputed_part_m, on='MSOA')
computing_measures(imputed_part, 'Women', 'Men', 'part')
    
    
#Voting for women
imputed_vote_w = pd.DataFrame({'MSOA':[], 'Women':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = women[women['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['l_vote7']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value, 'index':[0]})
    imputed_vote_w = pd.concat([imputed_vote_w, imputed_dict])
     
#Voting for men
men = us12_dist[us12_dist['l_sex']==1]
imputed_vote_m = pd.DataFrame({'MSOA':[], 'Men':[]})

for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = men[men['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['l_vote7']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Men':imputed_value, 'index':[0]})
    imputed_vote_m = pd.concat([imputed_vote_m, imputed_dict])
        
imputed_vote = imputed_vote_w.merge(imputed_vote_m, on='MSOA')
computing_measures(imputed_vote, 'Women', 'Men', 'vote')

#Exporting the results
imputed_part.to_csv('part_computed.csv')
imputed_vote.to_csv('vote_computed.csv')

