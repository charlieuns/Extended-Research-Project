import pandas as pd
import numpy as np
from index_functions import computing_measures

#A script to take in data from the GM residents' survey and compute the indicator measures from it

#These files are not open licence and so couldn't be made publically available in this repository
opp_by_IMD = pd.read_csv("/Users/charlieunsworth/Documents/Python Directories/ERP/GMCA_csv/opp_by_IMD.csv")
good_use_by_IMD = pd.read_csv("/Users/charlieunsworth/Documents/Python Directories/ERP/GMCA_csv/good_use_by_IMD.csv")
good_use_by_LA = pd.read_csv("/Users/charlieunsworth/Documents/Python Directories/ERP/GMCA_csv/good_use_by_LA.csv")
opp_by_LA = pd.read_csv("/Users/charlieunsworth/Documents/Python Directories/ERP/GMCA_csv/opp_by_LA.csv")

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

IMD_levels = list(('Least deprived',
                   '2',
                   '3',
                   '4',
                   'Most deprived'))


#Defining a function to relabel and deal with suppression
#Suppression was necessary for values under 5, and as such a replacement value of 3 was used
def cleaning(df, label_list, replacement_name):
    #Replace stars in values
    df = df.replace(to_replace='*', value=3)
    
    #Moving breakdown out of main column
    df['breakdown'] = 'none'
    for i in range(len(df)):
        if df['Unnamed: 0'][i] in label_list:
            df['breakdown'][i] = 'Total'
        elif df['Unnamed: 0'][i] == 'A man (including trans man)':
            df['breakdown'][i] = 'Men'
        else:
            df['breakdown'][i] = 'Women'

    #Setting the index
    df = df.replace(to_replace=['A man (including trans man)', 'A woman (including trans woman)'], method='ffill')
    df[replacement_name] = df['Unnamed: 0']
    df = df.drop(columns='Unnamed: 0')
    df = df.set_index([replacement_name,'breakdown'])
    
    return df

opp_by_IMD_clean = cleaning(opp_by_IMD, IMD_levels, 'IMD')
good_use_by_IMD_clean = cleaning(good_use_by_IMD, IMD_levels, 'IMD')
opp_by_LA_clean = cleaning(opp_by_LA, GM_LAs, 'LA')
good_use_by_LA_clean = cleaning(good_use_by_LA, GM_LAs, 'LA')

#Recoding data to a binary for both indicators
#Proportion agreeing with 'your job makes good use of your skills and abilities'
#Proportion reporting a postitive number of professional development or training opportunities in the last 12 months
good_use_by_IMD_clean['prop_agree'] = (good_use_by_IMD_clean['Strongly agree']+good_use_by_IMD_clean['Agree'])/good_use_by_IMD_clean.sum(axis=1, numeric_only=True)
good_use_by_LA_clean['prop_agree'] = (good_use_by_LA_clean['Strongly agree']+good_use_by_LA_clean['Agree'])/good_use_by_LA_clean.sum(axis=1, numeric_only=True)
opp_by_IMD_clean['prop_positive'] = 1 - opp_by_IMD_clean['None']/opp_by_IMD_clean.sum(axis=1, numeric_only=True)
opp_by_LA_clean['prop_positive'] = 1 - opp_by_LA_clean['None']/opp_by_LA_clean.sum(axis=1, numeric_only=True)

IMD_var = good_use_by_IMD_clean.reset_index()
IMD_var[IMD_var['breakdown']=='Total']['prop_agree'].var()

LA_var = good_use_by_LA_clean.reset_index()
LA_var[LA_var['breakdown']=='Total']['prop_agree'].var()
#Very low variance by IMD status meant that the IMD data was dropped from the analysis
#The imputation proceeds with just LA disaggregated data

#Restructuring the data to pass into the computing_measures function (see index_functions.py)
good_use = good_use_by_LA_clean.reset_index().pivot(index='LA', columns='breakdown', values='prop_agree')
opportunities = opp_by_LA_clean.reset_index().pivot(index='LA', columns='breakdown', values='prop_positive')

computing_measures(good_use, 'Women', 'Men', 'use_skills')    
computing_measures(opportunities, 'Women', 'Men', 'dev_opps')

#Imputing those measures from LAD to MSOA level
LA_MSOA_lookup = pd.read_csv('LA_MSOA_lookup.csv')
GM_only = LA_MSOA_lookup[LA_MSOA_lookup['GM']]

good_use_MSOA = GM_only.merge(good_use[['w_use_skills',
                                        'm_use_skills',
                                        'g_use_skills']],
                              left_on ='LAD22NM',
                              right_on = 'LA')
opportunities_MSOA = GM_only.merge(opportunities[['w_dev_opps',
                                                  'm_dev_opps',
                                                  'g_dev_opps']],
                                   left_on ='LAD22NM',
                                   right_on = 'LA')


good_use_MSOA['MSOA'] = good_use_MSOA['MSOA21CD']
opportunities_MSOA['MSOA'] = opportunities_MSOA['MSOA21CD']

good_use_df = good_use_MSOA[['MSOA', 'w_use_skills', 'm_use_skills', 'g_use_skills']]
opportunities_df = opportunities_MSOA[['MSOA', 'w_dev_opps', 'm_dev_opps', 'g_dev_opps']]

#Exporting the resulting files for aggregation
good_use_df.to_csv('gw_computed.csv')
opportunities_df.to_csv('po_computed.csv')

