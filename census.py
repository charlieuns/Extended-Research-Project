import pandas as pd
from index_functions import computing_measures

#A script to take census datasets, manipulate and compute the indices from them
#All data are available at: https://www.ons.gov.uk/datasets/create
employment_raw = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Census_datasets/economic_activity_age.csv')

occupation_raw = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Census_datasets/occupational_status_age.csv')

disability = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Census_datasets/disability.csv')

unpaid_care = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Census_datasets/unpaid_care.csv')

qualification = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Census_datasets/highest_qualification.csv')

home_equity = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Census_datasets/home_equity.csv')

general_health = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Census_datasets/general_health.csv')

GM_lookup = pd.read_csv('GM_LA_MSOA_lookup.csv')
GM_MSOAs = GM_lookup['MSOA21CD'].tolist()

#Defining custom functions to deal with the structure of the census datasets
#Firstly to pivot the data for a breakdown by sex
def custom_pivot(df, column):
    df_GM = df[df['Middle layer Super Output Areas Code'].isin(GM_MSOAs)]
    df_pivot = df_GM.pivot(columns=[column], 
                           index=['Middle layer Super Output Areas Code','Sex (2 categories)'],
                           values='Observation')
    return df_pivot

#Secondly to deal with the index and pass the data through computing_measures
def compute_census(df, indicator):
    df.reset_index(inplace=True)
    df_re_pivot = df.pivot(columns='Sex (2 categories)',
                           index = 'Middle layer Super Output Areas Code',
                           values = 'prop') 
    computing_measures(df_re_pivot, 'Female', 'Male', indicator)
    df_re_pivot.reset_index(inplace=True, names='MSOA')
    df_clean = df_re_pivot[['MSOA', 'w_' + indicator, 'm_' + indicator, 'g_' + indicator]]
    return df_clean

#Restricting work domains to just 18-64 year olds before they can be computed
ages =[2,3,4,5]
employment_working_age = employment_raw[employment_raw['Age (6 categories) Code'].isin(ages)]
employment_status = employment_working_age.groupby(['Middle layer Super Output Areas Code',
                                                    'Sex (2 categories)', 
                                                    'Economic activity status (7 categories) Code'])['Observation'].sum()
employment_status = employment_status.to_frame().reset_index()

occupation_working_age = occupation_raw[occupation_raw['Age (6 categories) Code'].isin(ages)]
occupation_status = occupation_working_age.groupby(['Middle layer Super Output Areas Code',
                                                    'Sex (2 categories)', 
                                                    'Occupation (current) (10 categories) Code'])['Observation'].sum()
occupation_status = occupation_status.to_frame().reset_index()


#Computing measures for all domains
#Proportion of working age people employed
employment_pivot = custom_pivot(employment_status, 'Economic activity status (7 categories) Code')
for i, row in employment_pivot.iterrows():
    prop = (row[1]+row[3])/row[1:7].sum()
    employment_pivot.loc[i,'prop'] = prop
employment_df = compute_census(employment_pivot, 'employment')
    
#Proportion of working age people in managerial, professional etc occupations
occupation_pivot = custom_pivot(occupation_status, 'Occupation (current) (10 categories) Code')
for i, row in occupation_pivot.iterrows():
    prop = (row[1:5].sum())/(row[1:10].sum())
    occupation_pivot.loc[i,'prop'] = prop
occupation_df = compute_census(occupation_pivot, 'occupation')
    
#Proportion of people considered to have a disability under the Equality Act 2010
disability_pivot = custom_pivot(disability, 'Disability (3 categories) Code')
for i, row in disability_pivot.iterrows():
    prop = row[1]/(row[1:3].sum())
    disability_pivot.loc[i, 'prop'] = prop
disability_df = compute_census(disability_pivot, 'disability')
    
#Proportion of people considered to be an unpaid carer
care_pivot = custom_pivot(unpaid_care, 'Unpaid care (5 categories) Code')
for i, row in care_pivot.iterrows():
    prop = row[2:5].sum()/row[1:5].sum()
    care_pivot.loc[i, 'prop'] = prop
care_df = compute_census(care_pivot, 'unpaid_care')
    
#Proportion of people holding a degree or higher
qual_pivot = custom_pivot(qualification, 'Highest level of qualification (7 categories) Code')
for i, row in qual_pivot.iterrows():
    prop = row[4]/row[1:7].sum()
    qual_pivot.loc[i, 'prop'] = prop
qual_df = compute_census(qual_pivot, 'highest_qual')

#Proportion of people who own their home  (either outright or with a mortgage)
home_pivot = custom_pivot(home_equity, 'Tenure of household (7 categories) Code')
for i, row in home_pivot.iterrows():
    prop = row[1:3].sum()/row[1:7].sum()
    home_pivot.loc[i, 'prop'] = prop
home_df = compute_census(home_pivot, 'home_equity')
    
#Proportion with good or very good self-percieved health
health_pivot = custom_pivot(general_health, 'General health (4 categories) Code')
for i, row in health_pivot.iterrows():
    prop = row[1]/row[1:4].sum()
    health_pivot.loc[i, 'prop'] = prop
health_df = compute_census(health_pivot, 'good_health')

#Exporting files for aggregtation    
employment_df.to_csv('computed/emp_computed.csv')
occupation_df.to_csv('computed/occ_computed.csv')
disability_df.to_csv('computed/dis_computed.csv')
care_df.to_csv('computed/care_computed.csv')
qual_df.to_csv('computed/qual_computed.csv')
home_df.to_csv('computed/he_computed.csv')
health_df.to_csv('computed/gh_computed.csv')



