#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 15:40:49 2025

@author: charlieunsworth
"""
import pandas as pd
from index_functions import computing_measures

#A script to take the names of councillors, estimate their gender and compute the indicator measure from that

#This file is available at: https://opencouncildata.co.uk/productsAndDownloads.php
councillor_names = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/opencouncildata_councillors.csv')

GM_LAs = list(('Bolton', 
              'Bury',
              'Manchester', 
              'Oldham', 
              'Rochdale', 
              'Salford', 
              'Stockport', 
              'Tameside', 
              'Trafford', 
              'Wigan'))

#Finding only councillors in Greater Manchester
GM_councillors = councillor_names[councillor_names['Council'].isin(GM_LAs)]

GM_councillors.to_csv('GM_councillors.csv')

#Used Namsor online API to apply morphological analysis of names
#tool available at: https://namsor.app/csv-excel-tool/
#This replicates exactly the proocess used by Schmid et al. (2025)
GM_councillors_w_predictions = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/namsor_genderize-full-name_GM_councillors.csv')
gender_dummies = pd.get_dummies(GM_councillors_w_predictions['likelyGender'])

GM_w_gender = GM_councillors.reset_index(names='ID')
GM_w_gender['predFemale'] = gender_dummies['female']

proportions = GM_w_gender.groupby('Council').agg(
    prop_female = pd.NamedAgg('predFemale', 'mean'))

proportions['prop_male'] = 1- proportions['prop_female']

computing_measures(proportions, 'prop_female', 'prop_male', 'council')

#Imputing the data from LAD to MSOA level and exporting it for aggregation
LA_MSOA_lookup = pd.read_csv('LA_MSOA_lookup.csv')
GM_only = LA_MSOA_lookup[LA_MSOA_lookup['GM']]
council_MSOA = GM_only.merge(proportions[['w_council',
                                          'm_council',
                                          'g_council']],
                              left_on ='LAD22NM',
                              right_on = 'Council')


council_MSOA['MSOA']=council_MSOA['MSOA21CD']
council_df = council_MSOA[['MSOA', 'w_council','m_council','g_council']]
council_df.to_csv('counc_computed.csv')


