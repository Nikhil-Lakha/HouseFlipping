import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import re

# Load data
property_list = pd.read_csv('all_property_details.csv', index_col=0)

# Cleaning Data
property_list = property_list.replace(to_replace='None', value=np.nan)
property_list = property_list.replace(to_replace='✔', value=1)

# Define functions for analysis and visualization
def calculate_nan_percentages(df):
    nan_percentages = (df.isna().sum() / len(df)) * 100
    nan_percentages_sorted = nan_percentages.sort_values(ascending=True)
    return nan_percentages_sorted

def filter_high_nan_columns(df, threshold=45):
    columns_to_remove = nan_percentages[nan_percentages >= threshold].index
    return df.drop(columns=columns_to_remove)

def clean_area_columns(df):
    df['Floor Area'] = df['Floor Area'].str.replace(r'Rates.*|None|LevyR.*|\xa0m²', '', regex=True)
    df['Land Area'] = df['Land Area'].str.replace(r'Rates.*|None|LevyR.*|\xa0m²', '', regex=True)
    return df

# Streamlit App
st.title('Market Analysis Dashboard')

# Display the raw data
st.subheader('Raw Data')
st.dataframe(property_list)

# Data Cleaning
st.subheader('Data Cleaning')

# Calculate and plot NaN percentages
nan_percentages_sorted = calculate_nan_percentages(property_list)
st.bar_chart(nan_percentages_sorted)

# Filter high NaN columns
property_list_cleaned = filter_high_nan_columns(property_list)

# Clean area columns
property_list_cleaned = clean_area_columns(property_list_cleaned)

# Display the cleaned data
st.subheader('Cleaned Data')
st.dataframe(property_list_cleaned)

# Data Analysis
st.subheader('Data Analysis')

# Group by suburb and area
suburb_areas = property_list_cleaned.groupby(['Suburb', 'Area']).size().reset_index(name='Count')

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

# Show the plot
st.plotly_chart(fig)

# Display Top 10 Apartments and Houses
st.subheader('Top 10 Apartments')
top_10_apartments = pd.read_csv('Top 10 Apartments.csv')
st.dataframe(top_10_apartments)

st.subheader('Top 10 Houses')
top_10_houses = pd.read_csv('Top 10 Houses.csv')
st.dataframe(top_10_houses)
