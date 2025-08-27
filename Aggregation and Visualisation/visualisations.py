#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  8 21:12:15 2025

@author: charlieunsworth
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

#A script to visualise the computed domains and overall indices, and compare them with GEIUK data

MSOA_df = pd.read_csv('GM_LA_MSOA_lookup.csv')
MSOA = pd.DataFrame()
MSOA['MSOA'] = MSOA_df['MSOA21CD']

#Reading in the shape data, available at: https://geoportal.statistics.gov.uk/datasets/ons::middle-layer-super-output-areas-december-2021-boundaries-ew-bgc-v3-2/about
filepath = 'Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V3_-3382097907403187870/MSOA_2021_EW_BSC_V3.shp'

shape_data = gpd.read_file(filepath)

GM_only_shapes = shape_data[shape_data['MSOA21CD'].isin(MSOA['MSOA'])]

#Using the files created in the aggregation (note GEIUK raw data is not licensed for this repository)
geiuk = pd.read_csv('geiuk_for_viz.csv')
subd_df = pd.read_csv('index_for_viz.csv')

shapes_geiuk = GM_only_shapes.merge(geiuk, left_on='MSOA21CD', right_on='MSOA21CD')
shapes_subd  = GM_only_shapes.merge(subd_df, left_on='MSOA21CD', right_on='MSOA')

#Aggregating computed data to make it comparable to GEIUK
shapes_subd_LA = shapes_subd.merge(MSOA_df, left_on='MSOA21CD', right_on='MSOA21CD')
LA_aggregates = shapes_subd_LA.groupby('LAD22NM').mean(numeric_only=True)
shapes_agg_LA = shapes_subd_LA.merge(LA_aggregates, left_on='LAD22NM', right_index=True)

#Generating figures 1-3 of the report
shapes_subd.plot(column='g_overall', vmin= 0.76, vmax=0.89).set_axis_off()
plt.savefig('fig1.png')
shapes_agg_LA.plot(column='g_overall_y', vmin= 0.76, vmax=0.89).set_axis_off()
plt.savefig('fig2.png')
shapes_geiuk.plot(column='index_g', legend=True, vmin= 0.76, vmax=0.89).set_axis_off()
plt.savefig('fig3.png')

#Figures 4-5
shapes_subd.plot(column='w_overall', vmin= 0.8, vmax=1.2).set_axis_off()
plt.savefig('fig4.png')
shapes_subd.plot(column='m_overall', legend=True, vmin= 0.8, vmax=1.2).set_axis_off()
plt.savefig('fig5.png')


#Figures 6-7
shapes_subd.plot(column='g_Money', vmin= 0.67, vmax=0.97).set_axis_off()
plt.savefig('fig6.png')
shapes_geiuk.plot(column='money_g', legend=True, vmin= 0.67, vmax=0.97).set_axis_off()
plt.savefig('fig7.png')


#Generating remaining figures for the appendix
domains = ['PaidWork','UnpaidWork','Money','PowerParticipation','Education','Health']
for i in domains:
    col_name = 'g_'+i
    file_name = 'g_'+i+'.png'
    shapes_subd.plot(column=col_name, legend=True).set_axis_off()
    plt.savefig(file_name)







