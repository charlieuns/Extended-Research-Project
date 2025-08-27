# Extended-Research-Project
A repository of additional materials in support of an Extended Research Project submitted to the University of Manchester for a degree in MSc Data Science


# Project Abstract
In this project, the methodology of the Gender Equality Index UK (Schmid et al., 2025) is extended from Local Authority District level down to Middle Super Output Area level in the Greater Manchester region. It builds on work which measures gender equality through a multi-dimensional index, generating new insight by offering a more granular unit of analysis. In the process, this work explores data availability at smaller geographies and considers the applicability of that data to the context of equality measurement. Further, the research evaluates existing techniques to generate small area estimates and develops a custom estimation procedure incorporating geographic boundaries with a Gaussian weighting function into a Boundary-Sensitive Neighbourhood Estimator. The success of these techniques is discussed, and the resulting indices computed to provide a uniquely granular insight into the topography of gender equality in Greater Manchester.


# Repository Structure
Data Files:
Folder with the dataset of final computed indicies ready for visualisation or other analysis, as well as all of the lookup files required to perform the estimation techniques detailed in the Estimation folder scripts. Indices starting with m_ refer to male attainment measures, w_ refer to female attainment and g_ refers to the equality measure.

Estimation:
Folder containing all of the scripts and details to perform Boundary-Sensitive Neighbourhood estimation. Also contains the details of the initial regression analyses and grid search sensitivity analysis which underpin the design of the estimator. See estimator_details for more information.

Other Domains:
Folder containing the scripts to wrangle and compute all other data sources which were not subject to the estimation procedure. Scripts are labelled according to their data source

Aggregation and Visualisation:
Folder with the scripts for the functions used to compute, aggregate and visualise the indices. Also included is an example choropleth visualisation for reference and an overview of the index structure to assist reproducability.
