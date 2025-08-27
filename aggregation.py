#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 20:25:37 2025

@author: charlieunsworth
"""
#A script to take in all the individual indicator files, aggregate them to sub-domains,
#domains and the overall measures, and then export them
import pandas as pd
import geopandas as gpd

csv_files = ['emp_computed.csv',
             'occ_computed.csv',
             'po_computed.csv',
             'gw_computed.csv',
             'care_computed.csv',
             'dl_computed.csv',
             'inc_computed.csv',
             'lp_computed.csv',
             'he_computed.csv',
             'll_computed.csv',
             'counc_computed.csv',
             'part_computed.csv',
             'vote_computed.csv',
             'qual_computed.csv',
             'edu_computed.csv',
             'le_computed.csv',
             'dis_computed.csv',
             'gh_computed.csv']

#Start with a column of the MSOAs, then merge each csv onto it in sequence, removing unnecessary columns
MSOA_df = pd.read_csv('GM_LA_MSOA_lookup.csv')
MSOA = pd.DataFrame()
MSOA['MSOA'] = MSOA_df['MSOA21CD']


final_index = MSOA
for i in csv_files:
    file_i = pd.read_csv('computed/'+i)
    file_i = file_i[file_i.columns.drop(file_i.filter(regex=r'(Unnamed|Men|Women|index|4567)'))]
    final_index = final_index.merge(file_i, on='MSOA')

#Index strings
index_str = ['w_','m_','g_']
subd_df = MSOA

#Iterating over women, men and the equality measure
for i in index_str:
    #Firstly subdomains
    subd_df[i+'Employment'] = (final_index[i+'employment'] + final_index[i+'occupation'])/2
    subd_df[i+'QualityWork'] = (final_index[i+'dev_opps'] + final_index[i+'use_skills'])/2
    subd_df[i+'CareDomestic'] = (final_index[i+'unpaid_care'] + final_index[i+'dom_lab'])/2
    subd_df[i+'Pay'] = (final_index[i+'income'] + final_index[i+'not_low_pay'])/2
    subd_df[i+'HomeEquity'] = final_index[i+'home_equity']
    subd_df[i+'Leadership'] = (final_index[i+'lead_ltd'] + final_index[i+'council'])/2
    subd_df[i+'Participation'] = (final_index[i+'part'] + final_index[i+'vote'])/2
    subd_df[i+'Qualifications'] = final_index[i+'highest_qual']
    subd_df[i+'NumeracyLiteracy'] = final_index[i+'gcses']
    subd_df[i+'LifeExpHealth'] = (final_index[i+'life_exp'] + final_index[i+'disability'] + final_index[i+'good_health'])/3

    #Then domains
    subd_df[i+'PaidWork'] = (subd_df[i+'Employment'] + subd_df[i+'QualityWork'])/2
    subd_df[i+'UnpaidWork'] = subd_df[i+'CareDomestic']
    subd_df[i+'Money'] = (subd_df[i+'Pay'] + subd_df[i+'HomeEquity'])/2
    subd_df[i+'PowerParticipation'] = (subd_df[i+'Leadership'] + subd_df[i+'Participation'])/2
    subd_df[i+'Education'] = (subd_df[i+'Qualifications'] + subd_df[i+'NumeracyLiteracy'])/2
    subd_df[i+'Health'] = subd_df[i+'LifeExpHealth']

    #Finally to the overall
    subd_df[i + 'overall'] = (subd_df[i+'PaidWork'] + subd_df[i+'UnpaidWork'] + subd_df[i+'Money'] + subd_df[i+'PowerParticipation'] + subd_df[i+'Education'] + subd_df[i+'Health'])/6

#Exporting the final result for visualisation, this file is available in this repository
subd_df.to_csv('index_for_viz.csv')






