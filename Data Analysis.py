#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
get_ipython().run_line_magic('matplotlib', 'widget')
import plotly.graph_objects as go
import re


# In[2]:


property_list = pd.read_csv('all_property_details.csv', index_col=0)
# Set display options for Pandas DataFrame
pd.set_option('display.max_colwidth', None)

# Display DataFrame
display(property_list)


# # Cleaning Data

# In[3]:


property_list = property_list.replace(to_replace='None', value=np.nan)
property_list = property_list.replace(to_replace='✔', value=1)
property_list.head()


# In[4]:


# Calculate the percentage of NaN values per column
nan_percentages = (property_list.isna().sum() / len(property_list)) * 100

# Sort the NaN percentages from highest to lowest
nan_percentages_sorted = nan_percentages.sort_values(ascending=True)

# Plotting the sorted percentages
nan_percentages_sorted.plot(kind='barh', color='skyblue', figsize=(20, 12))

plt.title('Percentage of NaN Values per Column')
plt.xlabel('Percentage of NaN')
plt.ylabel('Columns')
plt.xlim(0, 100)

# Adding the percentage values on the right of each bar
for i in range(len(nan_percentages_sorted)):
    plt.text(x=nan_percentages_sorted[i] + 1, y=i, s=f'{nan_percentages_sorted[i]:.2f}%', va='center')

plt.tight_layout()
plt.show()


# In[5]:


# Filter columns where percentage of NaN is 60% or more
columns_to_remove = nan_percentages[nan_percentages >= 45].index
# Remove the filtered columns
property_list = property_list.drop(columns=columns_to_remove)


# In[6]:


property_list.head()


# In[7]:


# Fixing the Floor Area and Land Area Columns

property_list['Floor Area'] = property_list['Floor Area'].str.replace(r'Rates.*|None|LevyR.*|\xa0m²', '', regex=True)
property_list['Land Area'] = property_list['Land Area'].str.replace(r'Rates.*|None|LevyR.*|\xa0m²', '', regex=True)


# In[8]:


property_list.head()


# In[9]:


property_list[['Bedrooms', 'Bathrooms', 'Price', 'Floor Area', 'Land Area','Lounges', 'Dining Areas','Pool']]


# In[11]:


# Convert specific columns to float data type after cleaning
columns_to_convert = ['Bedrooms', 'Bathrooms', 'Price', 'Floor Area', 'Land Area','Lounges', 'Dining Areas', 'Pool', 'Garages']

for column in columns_to_convert:
    # Remove commas and spaces before converting to float
    property_list[column] = pd.to_numeric(property_list[column].str.replace(',', '').str.replace(' ', ''), errors='coerce')


# In[12]:


property_list.dtypes


# In[13]:


# 1. Price per Square Meter:
property_list['Price per Sqm'] = property_list['Price'] / property_list['Floor Area']

#2. Price per Land Area:
property_list['Price per Land Area'] = property_list['Price'] / property_list['Land Area']

pattern = r'(Flat|House|Apartment)'

# Extract property type using regular expression
property_list['Type'] = property_list['Title'].str.extract(pattern)


# In[14]:


property_list.head()


# # Data Analysis

# In[15]:


# Group by suburb and area
suburb_areas = property_list.groupby(['Suburb', 'Area']).size().reset_index(name='Count')

# Create an interactive bar chart for suburbs
fig = go.Figure()

# Add bars for each suburb
for suburb in suburb_areas['Suburb'].unique():
    areas = suburb_areas[suburb_areas['Suburb'] == suburb]['Area']
    counts = suburb_areas[suburb_areas['Suburb'] == suburb]['Count']
    fig.add_trace(go.Bar(name=suburb, x=areas, y=counts, marker_color='rgb(158,202,225)'))

# Update layout
fig.update_layout(barmode='stack',
                  title='Number of Listings by Suburb and Area',
                  xaxis_title='Area',
                  yaxis_title='Number of Listings',
                  xaxis=dict(categoryorder='total descending'),
                  showlegend=True,
                  plot_bgcolor='rgba(0,0,0,0)',
                  paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Arial, sans-serif', size=12, color='darkslategray'))

# Add interactivity
fig.update_layout(updatemenus=[{
    'buttons': [{
        'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
        'label': 'Play',
        'method': 'animate'
    }],
    'direction': 'left',
    'pad': {'r': 10, 't': 87},
    'showactive': False,
    'type': 'buttons',
    'x': 0.1,
    'xanchor': 'right',
    'y': 0,
    'yanchor': 'top'
}])

# Show the plot
fig.show()


# In[16]:


import numpy as np

# Function to calculate min, max, average price, and corresponding href for a given title and floor size
def calculate_price_stats(row):
    title = row['Title']
    floor_size = row['Floor Area']
    
    try:
        # Filter properties matching the title
        filtered_properties = property_list[property_list['Title'] == title]
        
        # If no match is found, return NaN values
        if filtered_properties.empty:
            return pd.Series([np.nan, np.nan])
        
        # Find the closest floor size
        closest_size = min(filtered_properties['Floor Area'], key=lambda x: abs(x - floor_size))
        
        # Filter properties matching the title and closest floor size
        closest_properties = filtered_properties[filtered_properties['Floor Area'] == closest_size]
        
        # If no match is found, return NaN values
        if closest_properties.empty:
            return pd.Series([np.nan, np.nan])
        
        # Compute statistics
        max_price_row = closest_properties.loc[closest_properties['Price'].idxmax()]
        max_price_href = max_price_row['Href']
        max_price = closest_properties['Price'].max()
        return pd.Series([max_price, max_price_href])
    
    except KeyError:
        return pd.Series([np.nan, np.nan])

# Apply the function to each row of the DataFrame
property_list[['Max Price', 'Max Price Href']] = property_list.apply(calculate_price_stats, axis=1)


# In[17]:


# Adding a Potential Profit Field

property_list['Potential Profit'] = property_list['Max Price'] - property_list['Price']


# In[18]:


# Define widgets
province_widget = widgets.Dropdown(
    options=['All'] + list(property_list['Province'].unique()),
    value='All',
    description='Province:'
)

city_widget = widgets.Dropdown(
    options=['All'] + list(property_list['City'].unique()),
    value='All',
    description='City:'
)

suburb_widget = widgets.Dropdown(
    options=['All'] + list(property_list['Suburb'].unique()),
    value='All',
    description='Suburb:'
)

area_widget = widgets.Dropdown(
    options=['All'] + list(property_list['Area'].unique()),
    value='All',
    description='Area:'
)

price_slider = widgets.FloatRangeSlider(
    min=property_list['Price'].min(),
    max=property_list['Price'].max(),
    step=10000,
    value=[property_list['Price'].min(), property_list['Price'].max()],
    description='Price Range:'
)

price_per_sqm_slider = widgets.FloatRangeSlider(
    min=property_list['Price per Sqm'].min(),
    max=property_list['Price per Sqm'].max(),
    step=100,
    value=[property_list['Price per Sqm'].min(), property_list['Price per Sqm'].max()],
    description='Price per Sqm Range:'
)

sorting_criteria_widget = widgets.Dropdown(
    options=['None', 'Price', 'Price per Sqm'],
    value='None',
    description='Sorting Criteria:'
)

sorting_order_widget = widgets.Dropdown(
    options=['Ascending', 'Descending'],
    value='Ascending',
    description='Sorting Order:'
)

apply_button = widgets.Button(description="Apply Filters")

# Define filtering function
def filter_dataframe(button_instance):
    clear_output(wait=True)
    filtered_df = property_list.copy()
    if province_widget.value != 'All':
        filtered_df = filtered_df[filtered_df['Province'] == province_widget.value]
    if city_widget.value != 'All':
        filtered_df = filtered_df[filtered_df['City'] == city_widget.value]
    if suburb_widget.value != 'All':
        filtered_df = filtered_df[filtered_df['Suburb'] == suburb_widget.value]
    if area_widget.value != 'All':
        filtered_df = filtered_df[filtered_df['Area'] == area_widget.value]
    filtered_df = filtered_df[(filtered_df['Price'] >= price_slider.value[0]) & (filtered_df['Price'] <= price_slider.value[1])]
    filtered_df = filtered_df[(filtered_df['Price per Sqm'] >= price_per_sqm_slider.value[0]) & (filtered_df['Price per Sqm'] <= price_per_sqm_slider.value[1])]
    
    # Apply sorting
    if sorting_criteria_widget.value != 'None':
        ascending = sorting_order_widget.value == 'Ascending'
        filtered_df = filtered_df.sort_values(by=sorting_criteria_widget.value, ascending=ascending)
    
    display(filtered_df)

# Attach event handler to apply button
apply_button.on_click(filter_dataframe)

# Display widgets
display(province_widget, city_widget, suburb_widget, area_widget, price_slider, price_per_sqm_slider,
        sorting_criteria_widget, sorting_order_widget, apply_button)

# Display initial DataFrame


# In[19]:


# Function to select top 10 lowest-priced properties by square meter and Potential Profit > 0
def top_10_lowest_price_by_sqm_and_profit(df):
    return df[(df['Potential Profit'] > 0)].groupby('Area').apply(lambda x: x.nsmallest(10, 'Price per Sqm'))

# Filter DataFrames by property types
house_properties = property_list[(property_list['Type'] == 'House')]
flat_properties = property_list[(property_list['Type'] == 'Flat')]
apartment_properties = property_list[(property_list['Type'] == 'Apartment')]

# Apply function to each filtered DataFrame
house_top_10 = top_10_lowest_price_by_sqm_and_profit(house_properties)
flat_top_10 = top_10_lowest_price_by_sqm_and_profit(flat_properties)
apartment_top_10 = top_10_lowest_price_by_sqm_and_profit(apartment_properties)


# In[20]:


apartment_top_10.to_csv('Top 10 Apartments.csv')
house_top_10.to_csv('Top 10 Houses.csv')


# In[ ]:




