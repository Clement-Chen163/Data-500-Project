# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 13:20:39 2020

@author: cleme
"""

import pandas as pd
import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt

"reads excel and inserts into dataframe"
def read_xls_and_insert(dataframe,download_url,row):
    df1=pd.read_excel(download_url)
    Total_felonies=[]
    for i in df1.iloc[row,-2:-21:-1]:
        Total_felonies.append(i)
    dataframe.insert(dataframe.shape[1],df1.iloc[row,0],Total_felonies)

def formatting():
    "reads .json into a pandas dataframe"
    df=pd.read_json ('https://data.cityofnewyork.us/resource/hukm-snmq.json')
    
    "shifts column 'category' from end to second to front"
    category_label=df.columns[-1]
    category_values=df.values.T[-1]
    df.drop(columns='category',inplace=(True))
    df.insert(1,category_label,category_values)
    
    "create a list of nan rows to drop and drop them"
    drop_list=[]
    for i in range(df.shape[0]):
        if pd.isna(df.iloc[i,2:]).all():
            drop_list.append(i)      
    df.drop(drop_list,inplace=True)
    
    "reset index"
    df=df.reset_index()
    df=df.drop('index',axis=1)
    
    "collapses 'agency_capital_expeditures_by_purpose' and 'categories' into one column"    
    "i feel like there is a fucntion for this"
    for i in range(df.shape[0]):
        if pd.isna(df.iloc[i,0]):
            df.iloc[i,0]=df.iloc[i,1] 
    df=df.drop('category',axis=1)
    
          
    "transpose dataframe"
    df=df.T
    
    "turn  row 0 into column labels"
    df.columns=df.iloc[0]
    df=df.drop('agency_capital_expenditures_by_purpose')
    
    "drop years 1985-1999"
    df=df.drop(df.index[-15:])
    
    "convert any strings to floats"
    characters_to_remove=", -"
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            if isinstance(df.iloc[i,j],str):
                df.iloc[i,j]=float(df.iloc[i,j].translate({ord(k): None for k in characters_to_remove}))
    
    "read .xls and inserts crime data"
    read_xls_and_insert(df,'https://www1.nyc.gov/assets/nypd/downloads/excel/analysis_and_planning/historical-crime-data/non-seven-major-felony-offenses-2000-2019.xls',12)
    read_xls_and_insert(df,'https://www1.nyc.gov/assets/nypd/downloads/excel/analysis_and_planning/historical-crime-data/seven-major-felony-offenses-2000-2019.xls',11)
    read_xls_and_insert(df,'https://www1.nyc.gov/assets/nypd/downloads/excel/analysis_and_planning/historical-crime-data/misdemeanor-offenses-2000-2019.xls',20)
    read_xls_and_insert(df,'https://www1.nyc.gov/assets/nypd/downloads/excel/analysis_and_planning/historical-crime-data/violation-offenses-2000-2019.xls',5)
    
    "sum and insert total offenses"
    df.insert(df.shape[1],'TOTAL OFFENSES',df[df.columns[-1:-5:-1]].sum(axis=1))
    
    "insert cpi data"
    url='https://github.com/Clement-Chen163/Data-500-Project/raw/master/SeriesReport-20200912221317_b698d5.xlsx'
    cpi=pd.read_excel(url)
    cpi_label=cpi.columns[0]
    cpi_list=[i for i in cpi.iloc[-2:-21:-1,1]]
    df.insert(df.shape[1],cpi_label,cpi_list) 
    
    "insert scaled cpi data"
    scaled_cpi_list=[df[df.columns[-1]][0]/i for i in df[df.columns[-1]]]
    df.insert(df.shape[1],'adj_2018', scaled_cpi_list)
    return df

def revised_dataframe_for_Elif():
    df=formatting().reset_index()
    df.insert(0,'fiscal year',[int(i[3:7]) for i in df['index']])
    df=df.drop('index',axis=1)
    df=df.set_index(['fiscal year'])
    df=df.sort_index()
    return df

def formatting_cpi():
    df=formatting()
    for i in range(61):
        df.iloc[:,i]=df.iloc[:,i]*df['adj_2018']
    return df
    
def revised_dataframe_for_Elif_cpi():
    df=revised_dataframe_for_Elif()
    for i in range(61):
        df.iloc[:,i]=df.iloc[:,i]*df['adj_2018']
    return df

def scatter_plot(df,Title=None):
    List_of_budget_totals=['TOTAL EDUCATION','TOTAL TRANSPORTATION SERVICES','TOTAL HOUSING AND ECONOMIC DEVELOPMENT','TOTAL PUBLIC SAFETY AND JUDICIAL','TOTAL SOCIAL SERVICES']
    xticks=np.arange(0,4,.5)
    yticks=np.arange(0,1000000,100000)
    x=np.array(df[Title]/1000000000).astype(float)
    y=np.array(df['TOTAL OFFENSES']).astype(float)
    plt.scatter(x,y)
    plt.ylabel('Total Offenses')
    capitalize= ' '.join([j.capitalize() for j in i.split(' ')])
    plt.xlabel(capitalize+' Budget in Billions')
    plt.title(capitalize+ ' Budget vs Total Offenses')
    plt.xticks(xticks)
    plt.yticks(yticks)
    b, m = polyfit(x, y, 1)
    plt.plot(x, b + m * x, '-')

def make_plots():
    List_of_budget_totals=['TOTAL EDUCATION','TOTAL TRANSPORTATION SERVICES','TOTAL HOUSING AND ECONOMIC DEVELOPMENT','TOTAL PUBLIC SAFETY AND JUDICIAL','TOTAL SOCIAL SERVICES']
    for i in List_of_budget_totals:
        scatter_plot(df,Title=i)
        plt.show()
        cov_matrix=np.cov(np.array(df[i]).astype(float),np.array(df['TOTAL OFFENSES']))
        rho=cov_matrix[0,1]/(np.sqrt(cov_matrix[0,0])*np.sqrt(cov_matrix[1,1]))
        print("The Pearson Correlation Coefficient is {coeff}".format(coeff=rho))
#"inserts TOTAL SEVEN MAJOR FELONY OFFENSES from 2000-2018"
#not sure why this doesnt work. didnt work before or after cutting 1985-1999
#df.insert(df.shape[1],df1.iloc[11,0],df1.iloc[11,-2:-21:-1])
#not sure if having float and np.float64 will interfere with analysis
# =============================================================================
# Total_seven_major_felonies=[]
# for i in df1.iloc[11,-2:-21:-1]:
#     Total_seven_major_felonies.append(i)
# df.insert(df.shape[1],df1.iloc[11,0],Total_seven_major_felonies)
# 
# =============================================================================

















        