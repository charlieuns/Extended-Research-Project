#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 15:28:47 2025

@author: charlieunsworth
"""
#A script to take in (fe)male-led companies data and compute the index measures from it
import pandas as pd
from index_functions import computing_measures

#Data available from: https://www.thegenderindex.co.uk/explore
companies_df = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/gender_index.csv')

#Cleaning the % symbols
for i in range(len(companies_df)):
    companies_df['% Female-led'][i] = float(companies_df['% Female-led'][i].replace("%",""))
    companies_df['% Male-led'][i] =float(companies_df['% Male-led'][i].replace("%",""))
    

computing_measures(companies_df, '% Female-led', '% Male-led', 'lead_ltd')

companies_df.set_index('Local authorities', inplace=True)

#Imputing from LAD to MSOA level
LA_MSOA_lookup = pd.read_csv('LA_MSOA_lookup.csv')
GM_only = LA_MSOA_lookup[LA_MSOA_lookup['GM']]

lead_ltd_MSOA = GM_only.merge(companies_df[['w_lead_ltd',
                                        'm_lead_ltd',
                                        'g_lead_ltd']],
                              left_on ='LAD22NM',
                              right_on = 'Local authorities')

#Exporting the results for aggregation
lead_ltd_MSOA['MSOA'] = lead_ltd_MSOA['MSOA21CD']
ll_df = lead_ltd_MSOA[['MSOA','w_lead_ltd','m_lead_ltd','g_lead_ltd']]
ll_df.to_csv('ll_computed.csv')