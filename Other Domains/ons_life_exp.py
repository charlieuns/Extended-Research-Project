#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 17:30:21 2025

@author: charlieunsworth
"""
#Script to take ons life expectancy data, impute it from LA to MSOA level and export the computed measures
import pandas as pd
from index_functions import computing_measures

#Data available at: https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/healthandlifeexpectancies/datasets/lifeexpectancyforlocalareasofgreatbritain
ons_life_expectancy = pd.read_csv('ons_life_expectancy.csv')

lookup = pd.read_csv('GM_LA_MSOA_lookup.csv')

#Imputation from LAD to MSOA
GM_life_exp = lookup.merge(ons_life_expectancy, left_on='LAD22CD', right_on='Area code')

computing_measures(GM_life_exp, 'Women', 'Men', 'life_exp')

GM_life_exp['MSOA'] = GM_life_exp['MSOA21CD']
life_exp_df = GM_life_exp[['MSOA','w_life_exp','m_life_exp','g_life_exp']]

life_exp_df.to_csv('le_computed.csv')
