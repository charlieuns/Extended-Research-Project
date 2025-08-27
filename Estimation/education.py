#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 18:17:22 2025

@author: charlieunsworth
"""

import numpy as np
import pandas as pd
from index_functions import computing_measures

#A script to take Department for Education data, estimate MSOA values using a custom estimation method and
#compute the index values for the Education domain

#Data available at: https://explore-education-statistics.service.gov.uk/find-statistics/key-stage-4-performance/2023-24
performance_national = pd.read_csv('202324_performance_tables_schools_final.csv')
#Data available at: https://get-information-schools.service.gov.uk/Search
MSOA_df_school = pd.read_csv('schools_MSOA.csv')

#Restricting to just the sex-disaggregated data
performance_by_sex = performance_national[performance_national['breakdown_topic']=='Sex']

linked_df = performance_by_sex.merge(MSOA_df_school,left_on='school_urn', right_on='URN')

cleaned_df = linked_df[['school_urn', 'school_name', 'sex',
                        'establishment_type_group', 't_entbasics' , 
                        't_gcse_e', 't_l2basics_95', 'MSOA (code)']]

#Cleaning the relevant columns
cleaned_df['t_entbasics'].replace(['z','c'], 0, inplace=True)
cleaned_df['t_l2basics_95'].replace(['z','c'], 0, inplace=True)

cleaned_df['t_entbasics'] = pd.to_numeric(cleaned_df['t_entbasics'])
cleaned_df['t_l2basics_95'] = pd.to_numeric(cleaned_df['t_l2basics_95'])

girls = cleaned_df[cleaned_df['sex']=='Girls']
girls.reset_index(inplace=True)
boys = cleaned_df[cleaned_df['sex']=='Boys']
boys.reset_index(inplace=True)


#Subsetting to only GM and neighbours
GM_neighbours_MSOAs = pd.read_csv('LA_MSOA_lookup.csv')
girls_GM = girls[girls['MSOA (code)'].isin(GM_neighbours_MSOAs['MSOA21CD'])]
boys_GM = boys[boys['MSOA (code)'].isin(GM_neighbours_MSOAs['MSOA21CD'])]


#Generating an observation for each student
girls_df = pd.DataFrame({'school':[],
          'passed_basics':[],
          'MSOA': []})
for index, row in girls_GM.iterrows():
    passes = row['t_l2basics_95']
    entries = row['t_entbasics']
    fails = entries - passes
    MSOA = row['MSOA (code)']
    school = row['school_name']
    for i in range(passes):
        dict_i = {'school':school,
                  'passed_basics':1,
                  'MSOA': MSOA}
        df_i = pd.DataFrame(dict_i, index=[0])
        girls_df = pd.concat([girls_df, df_i])
    for i in range(fails):
        dict_i = {'school': school,
                  'passed_basics':0,
                  'MSOA': MSOA}
        df_i = pd.DataFrame(dict_i, index=[0])
        girls_df = pd.concat([girls_df, df_i])
girls_df.reset_index(drop =True, inplace=True)    
girls_df.to_csv('girls_df.csv')

#Repeated for boys
boys_df = pd.DataFrame({'school':[],
          'passed_basics':[],
          'MSOA': []})
for index, row in boys_GM.iterrows():
    passes = row['t_l2basics_95']
    entries = row['t_entbasics']
    fails = entries - passes
    MSOA = row['MSOA (code)']
    school = row['school_name']
    for i in range(passes):
        dict_i = {'school':school,
                  'passed_basics':1,
                  'MSOA': MSOA}
        df_i = pd.DataFrame(dict_i, index=[0])
        boys_df = pd.concat([boys_df, df_i])
    for i in range(fails):
        dict_i = {'school': school,
                  'passed_basics':0,
                  'MSOA': MSOA}
        df_i = pd.DataFrame(dict_i, index=[0])
        boys_df = pd.concat([boys_df, df_i])
boys_df.reset_index(drop =True, inplace=True) 
boys_df.to_csv('boys_df.csv')  
    
#Preparing for imputation
neighbours = pd.read_csv('MSOA_neighbours_50.csv')

girls_dist = neighbours.merge(girls_df, left_on='MSOA21CD_dest', right_on='MSOA')
girls_dist.to_csv('girls_dist.csv')
boys_dist = neighbours.merge(boys_df, left_on='MSOA21CD_dest', right_on='MSOA')

#Iterating over the MSOAs to apply the estimation procedure, see estimation_details for more
from edited_imputer import assign_weights

imputed_girls = pd.DataFrame({'MSOA':[], 'Women':[]})
for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = girls_dist[girls_dist['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['passed_basics']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Women':imputed_value, index:[0]})
    imputed_girls = pd.concat([imputed_girls, imputed_dict])
    
imputed_boys = pd.DataFrame({'MSOA':[], 'Men':[]})
for i in neighbours['MSOA21CD_origin'].unique():
    subset_i = boys_dist[boys_dist['MSOA21CD_origin']==i]
    sd = subset_i['dist'].std()
    subset_weighted = assign_weights(subset_i, sd, 0.9)
    imputed_value = (subset_weighted['norm_weight']*subset_weighted['passed_basics']).sum()
    imputed_dict = pd.DataFrame({'MSOA':i, 'Men':imputed_value, index:[0]})
    imputed_boys = pd.concat([imputed_boys, imputed_dict])

#Rejoining and computing final measures to export
imputed_df = imputed_girls.merge(imputed_boys, on='MSOA')
computing_measures(imputed_df, 'Women', 'Men', 'gcses')
imputed_df.to_csv('edu_computed.csv')


