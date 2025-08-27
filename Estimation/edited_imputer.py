# -*- coding: utf-8 -*-
"""
Created on Sat Aug  2 14:56:49 2025

@author: b60091cu
"""

import numpy as np
import math
import pandas as pd

"""
A script to firstly compute a set of nearest neighbour MSOAs from which to estimate the MSOA values
and secondly to define a weighting function for use in each of the estimation instances
"""

#These files are provided in the repository, they contain computed distances between MSOAs
#and lookups from MSOA to LAD level respectively
distances = pd.read_csv("MSOA_distances.csv")
GM_MSOAs = pd.read_csv("GM_LA_MSOA_lookup.csv")

#Finding only MSOAs within Greater Manchester which need to have neighbours assigned
GM_only = GM_MSOAs['MSOA21CD'].tolist()

GM_dist = distances[distances['MSOA21CD_origin'].isin(GM_only)]
GM_dist.to_csv("GM_dist.csv")

#A function is used to allow flexibility primarily in the number of neighbours assigned
def neighbours(distances, n_neighbours):
    neighbours_df = pd.DataFrame({'MSOA21CD_origin':[], 
            'MSOA21CD_dest': [],
            'dist':[]})
    distances.sort_values('dist', inplace=True)

    for i in GM_only:
        distances_i = distances[distances['MSOA21CD_origin']==i]
        subset_i = distances_i.nsmallest(n_neighbours, 'dist')
        dict_i = {'MSOA21CD_origin':i, 
                'MSOA21CD_dest': subset_i['MSOA21CD_dest'],
                'dist': subset_i['dist']}
        df_i = pd.DataFrame(dict_i)
        neighbours_df = pd.concat([neighbours_df, df_i])
    return neighbours_df

#100 neighbours were used for Understanding Society data
MSOA_neighbours = neighbours(GM_dist, 100)

#Joining and rejoining the dataframes to compare the LAs of origin and destination (estimated and neighbour)
#MSOAs, creating a dummy for same LA which is later used in the weighing process
MSOA_LA = MSOA_neighbours.merge(GM_MSOAs, left_on='MSOA21CD_origin', right_on='MSOA21CD')
MSOA_LA.rename(columns={'LAD22CD': 'LA_origin'}, inplace=True)
MSOA_LA = MSOA_LA.merge(GM_MSOAs, left_on='MSOA21CD_dest', right_on='MSOA21CD')
MSOA_LA.rename(columns={'LAD22CD': 'LA_dest'}, inplace=True)

MSOA_LA['same_LA'] = pd.to_numeric(MSOA_LA['LA_origin'] == MSOA_LA['LA_dest'])
MSOA_LA = MSOA_LA[['MSOA21CD_origin', 'MSOA21CD_dest', 'dist', 'same_LA']]

#Exporting the result, this file is given in the repository
MSOA_LA.to_csv('MSOA_neighbours_100.csv')


#Defining the weighting function which will be used to estimate MSOA values for both Understanding Society
#and Department for Education data
def assign_weights(subset_i, sd, penalty):
    a = 1/ np.sqrt(2*(math.pi)*(sd**2))
    b = -1/(2*(sd**2))
    #Firstly the density of the gaussian is computed
    subset_i['gauss_weight'] = a * math.e**(b*subset_i['dist']**2)
    #Then the blocking procedure is applied
    subset_i['blocked_weight'] = np.where(subset_i['same_LA']==True,
                                          subset_i['gauss_weight'],
                                          subset_i['gauss_weight']*penalty)
    #Finally the weights are normalised
    subset_i['norm_weight'] = subset_i['blocked_weight']/(subset_i['blocked_weight'].sum())
    return subset_i

#For technical details of the estimator see estimator_details in the main branch
