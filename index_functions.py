#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 16:14:57 2025

@author: charlieunsworth
"""
import pandas as pd
import numpy as np

#A script to take the measures for men and women and compute the three index values for them
def computing_measures(df, Women_col, Men_col, indicator):
    #Relies on a standardised format for the columns and a string for the indicator
    #Note that it edits the DataFrame in place
    df['w_' + indicator] = df[Women_col] / df[Women_col].mean()
    df['m_' + indicator] = df[Men_col] / df[Men_col].mean()
    df['g_' + indicator] = np.where(df[Men_col]<df[Women_col], df[Men_col]/df[Women_col], df[Women_col]/df[Men_col])

  


