#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 500)


# In[2]:


import seaborn as sns
import matplotlib.pyplot as plt
#%matplotlib inline


# In[3]:


import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs,init_notebook_mode,plot,iplot
init_notebook_mode(connected=True)


# # Scrap Data From The Github Site (Link Below)

# Github Data API - https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.json
# Github Repository of Police Brutality - https://github.com/2020PB/police-brutality/blob/master/README.md

# In[4]:


pb_data_raw = pd.read_json(r'https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.json')


# In[5]:


usa_state_pop2019 = pd.read_csv(r'C:\Users\cdwhi\Documents\Python\My_Code\Police_Brutality_2020\2019_USA_Population_Data.csv')


# # Tests on Data

# In[6]:


# Check of number of records in repository
len(pb_data_raw)


# # Set data up into proper matrix format 

# In[7]:


# creates a dictionary from the List of Data Frame Names (Keys) and the Data Frame Files (Values) themselves
dict_of_pb_dfs = {}

for pb_record_idex_num in range(0,len(pb_data_raw['data'])): 
    globals()["pb_df_{}".format(pb_record_idex_num)]  = pd.DataFrame(pb_data_raw['data'][pb_record_idex_num])
    dict_of_pb_dfs["pb_df_{}".format(pb_record_idex_num)] = globals()["pb_df_{}".format(pb_record_idex_num)]
    
# Reduces the record numbers to 1 per incident in each data frame
for pb_df in dict_of_pb_dfs.keys():
    num_count = len(dict_of_pb_dfs[pb_df])-1
    while num_count > 0:
        dict_of_pb_dfs[pb_df].drop(num_count, inplace = True)
        num_count -= 1
        
# Concatenate the individual data frames into one dataframe with all the incident data (one link/record per incident)
list_of_values = list(dict_of_pb_dfs.values())
pd_consolidated = pd.concat(list_of_values, sort = True)
pd_consolidated['incident_value'] = 1


# In[8]:


by_state = pd_consolidated.groupby('state')
by_state_sum_incidents = by_state.sum()




# Set up Data Frame for State Population      
state_pop_df = pd.DataFrame(columns=['state','population'])
for state in list(by_state_sum_incidents['incident_value'].index):
    #print(state)
    if state in list(usa_state_pop2019["NAME"]):
        #print(state)
        #print(usa_state_pop2019[usa_state_pop2019["NAME"] == state]["POPESTIMATE2019"].values[0])
        state_pop_df = state_pop_df.append({'state': state, 'population': usa_state_pop2019[usa_state_pop2019["NAME"] == state]["POPESTIMATE2019"].values[0]}, 
                                           ignore_index =True)

        
# Set up Data Frame for Incident Count Per State
state_pb_per_capita = pd.DataFrame(columns=['state','incident_count','population','incident_per_capita'])
for index_num in range(0,len(by_state_sum_incidents['incident_value'].index)):
    per_capita_pb_incidents = by_state_sum_incidents['incident_value'].values[index_num]/state_pop_df['population'].values[index_num]
    if by_state_sum_incidents.index[index_num] in list(usa_state_pop2019["NAME"]):
        state = by_state_sum_incidents.index[index_num]
        state_pb_per_capita = state_pb_per_capita.append({'state':by_state_sum_incidents.index[index_num],
                                                          'incident_count': by_state_sum_incidents['incident_value'].values[index_num],
                                                          'population': state_pop_df['population'].values[index_num],
                                                          'incident_per_capita':per_capita_pb_incidents},
                                                         ignore_index =True)

# Set up dictionary for the Plotly Map Text      
dict_of_incident_names = {}

for state in by_state_sum_incidents['incident_value'].keys():
    #print(state)
    dict_of_incident_names[state] = {}
    pb_query = pd_consolidated['state'] == state
    #print(pd_consolidated[pb_query]['links'])
    dict_of_incident_names[state] = pd_consolidated[pb_query]['name']

array_pb_incident_names = np.array(list(dict_of_incident_names.values()))

by_date = pd_consolidated.groupby('date')
by_date_sum_incidents = by_date.sum()
first_date = by_date_sum_incidents.index[1]
last_date = by_date_sum_incidents.index[len(by_date_sum_incidents.index)-1]

fig = go.Figure(data=[go.Bar(
    x=state_pb_per_capita['state'],
    y=state_pb_per_capita['incident_per_capita'],
    marker_color= 'black',
    name = 'Police Brutality Incident Counts Divided by State Population',
    text = state_pb_per_capita['population'],
    hovertext = state_pb_per_capita['incident_count'],
    #customdata = ,
    hovertemplate = "State: %{x}<br>Incident Counts: %{hovertext}<br>Population: %{text}<br>Per Captita Incident Count: %{y}<extra></extra>",
    width = .8,
    showlegend = True,
)])

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

fig.update_layout(title_text = '2020 Police Brutality: {} Incidents Captured on Video<br>Data from {} to {}<br>Date Created: {}'.format(len(pb_data_raw),first_date,last_date,dt_string),
                  xaxis_tickangle=-45,
                  autosize=True,
#                   width=1500,
#                   height=1200,
                  legend_orientation="v",
                  legend=dict(x=.875, y=0.99)
                 )

fig.write_html(r"C:\Users\cdwhi\Documents\Python\My_Code\Police_Brutality_2020\PB_2020_Bar_Graph_Incidents_by_State_per_Population\index.html")
fig.show()


# In[ ]:





# In[ ]:




