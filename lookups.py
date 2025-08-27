import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

#A script to gather relevant area lookup tables, associate them with shapefiles for visualisation
#and compute distances for use in the estimation procedure

#MSOA to LA lookups, available at: https://www.data.gov.uk/dataset/da36cac8-51c4-4d68-a4a9-37ac47d2a4ba/msoa-2011-to-msoa-2021-to-local-authority-district-2022-exact-fit-lookup-for-ew-v2
MSOA_lookup = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/MSOA_lookup.csv')

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

#Neighbouring LAD areas to be used in the estimation process, see us_linkage12 and us_linkage14
neighbouring_LAs = list(('Rossendale',
                        'Calderdale',
                        'Kirklees',
                        'High Peak',
                        'Cheshire East',
                        'Warrington',
                        'St Helens',
                        'West Lancashire',
                        'Chorley',
                        'Blackburn with Darwen'))

GM_plus_neighbours = GM_LAs + neighbouring_LAs

MSOA_GM = MSOA_lookup[MSOA_lookup['LAD22NM'].isin(GM_plus_neighbours)]

MSOA_GM['GM'] = MSOA_GM['LAD22NM'].isin(GM_LAs)

MSOA_GM_only = MSOA_GM[MSOA_GM['GM'] == True]


#Loading the shapefiles, available at: https://geoportal.statistics.gov.uk/datasets/ons::middle-layer-super-output-areas-december-2021-boundaries-ew-bgc-v3-2/about
filepath = '/Users/charlieunsworth/Documents/Python Directories/ERP/Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BSC_V3_-3382097907403187870/MSOA_2021_EW_BSC_V3.shp'

shape_data = gpd.read_file(filepath)

shape_data.plot()

shape_data['centroid'] = shape_data['geometry'].centroid

GM_neighbours_shapes = shape_data[shape_data['MSOA21CD'].isin(MSOA_GM['MSOA21CD'])]

GM_only_shapes = shape_data[shape_data['MSOA21CD'].isin(MSOA_GM_only['MSOA21CD'])]

#Testing the data for plotting, see visualisations
GM_only_shapes.plot()


#LSOA 2021 to MSOA 2021 lookups, available at: https://geoportal.statistics.gov.uk/datasets/b9ca90c10aaa4b8d9791e9859a38ca67_0/explore
MSOA_LSOA_lookup = pd.read_csv('/Users/charlieunsworth/Documents/Python Directories/ERP/Output_Area_to_Lower_layer_Super_Output_Area_to_Middle_layer_Super_Output_Area_to_Local_Authority_District_(December_2021)_Lookup_in_England_and_Wales_v3.csv')

#Getting co-ordinates and computing distances between MSOAs by joining and rejoining DataFrames
cross_join = pd.merge(MSOA_GM['MSOA21CD'], MSOA_GM['MSOA21CD'], how='cross', suffixes=('_origin','_dest'))
joined_origin = cross_join.merge(shape_data, left_on='MSOA21CD_origin', right_on='MSOA21CD')
joined_origin.rename(columns={'centroid':'origin_point'}, inplace=True)
joined_dest = joined_origin.merge(shape_data, left_on='MSOA21CD_dest', right_on='MSOA21CD')
joined_dest.rename(columns={'centroid':'dest_point'}, inplace=True)

cleaned_coords = joined_dest[['MSOA21CD_origin', 'MSOA21CD_dest', 'origin_point', 'dest_point']]

dist = []
for i in range(len(cleaned_coords)):
    dist.append(cleaned_coords['origin_point'][i].distance(cleaned_coords['dest_point'][i]))

cleaned_coords['dist'] = dist

#Exporting files for use in other scripts, all available in the repository
cleaned_coords.to_csv('MSOA_distances.csv')
MSOA_LSOA_lookup.to_csv('MSOA_LSOA_lookup.csv')
MSOA_GM.to_csv('LA_MSOA_lookup.csv')
MSOA_GM_only.to_csv('GM_LA_MSOA_lookup.csv')

