import streamlit as st
import pandas as pd
import plotly.express as px
import os
import matplotlib.pyplot as plt

def main():

    tab1, tab2, tab3 = st.tabs(["Listed Homes", "Sold Homes", "Marketing Research"])

    with tab1:
        # Load data
        file_path = "https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/master/Listed%20Properties/Current%20Listed%20Properties.csv"
        df = pd.read_csv(file_path)

        # Default columns to display
        default_columns = ['tile', 'href','property_type', 'Bedrooms', 'Bathrooms', 'price', 'Floor Area', 'Province', 'City', 'Suburb', 'Area', "Price per sqm"]

        # Sidebar for selecting columns
        st.sidebar.title("Column Selection")

        # Filter out default columns that don't exist in the dataframe
        default_columns = [col for col in default_columns if col in df.columns]

        selected_columns = st.sidebar.multiselect("Select Columns", df.columns.tolist(), default=default_columns)
        

    
        # Filter options
        province_options = ['gauteng'] + list(df['Province'].unique())
        city_options = ['All']
        suburb_options = ['All']
        area_options = ['All']

        col1, col2, col3, col4 = st.columns(4)
        

    

        # Sidebar filters
        with col1:
            province_selected = st.selectbox('Select Province', province_options)

        with col2:
            if province_selected != 'All':
                city_options = ['All'] + list(df[df['Province'] == province_selected]['City'].unique())
            city_selected = st.selectbox('Select City', city_options)

        with col3:
            if city_selected != 'All':
                suburb_options = ['All'] + list(df[(df['Province'] == province_selected) & (df['City'] == city_selected)]['Suburb'].unique())
            suburb_selected = st.selectbox('Select Suburb', suburb_options)

        with col4:
            if suburb_selected != 'All':
                area_options = ['All'] + list(df[(df['Province'] == province_selected) & (df['City'] == city_selected) & (df['Suburb'] == suburb_selected)]['Area'].unique())
            area_selected = st.selectbox('Select Area', area_options)

        # Filter dataframe based on selected options and price range
        filtered_df = df[
            (df['Province'] == province_selected if province_selected != 'All' else True) &
            (df['City'] == city_selected if city_selected != 'All' else True) &
            (df['Suburb'] == suburb_selected if suburb_selected != 'All' else True) &
            (df['Area'] == area_selected if area_selected != 'All' else True)
        ]

        
        col1, col2 = st.columns(2)


        with col1:
        # Display filtered dataframe with selected columns
            st.write(filtered_df[selected_columns])

        
        # Create a plotly figure
            fig = px.scatter(
            filtered_df,
            x='price',
            y='Price per sqm',
            color='Area',  # Color by Suburb
            hover_name='title',
            text = 'Bedrooms',
            size = 'Bedrooms'
    )
        fig.update_layout(
        clickmode='event+select',  # Enable click interaction
        legend=dict(
        orientation='h',  # Horizontal orientation
        yanchor='top',      # Anchor to the top
        y=1.1               # Position slightly above the plot
    )
)  # Enable click interaction

        with col2:
            fig.update_traces(textfont_color='white')
        # Use st.plotly_chart to display the interactive plot
            st.plotly_chart(fig, use_container_width=True)

    with tab2:

        # Function to process each CSV file
        def process_csv(file):
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file)
            
            # Remove duplicates based on "List ID" column, keeping the oldest "Sold Date"
            df['Sold Date'] = pd.to_datetime(df['Sold Date'])  # Convert 'Sold Date' to datetime
            df.sort_values(by='Sold Date', inplace=True)  # Sort by 'Sold Date' to get the oldest first
            df.drop_duplicates(subset='Listing Number', keep='first', inplace=True)
            
            return df

        # Define the directory where the CSV files are located
        directory = 'https://github.com/Nikhil-Lakha/HouseFlipping/tree/master/Sold%20Properties'

        # List to store processed DataFrames
        dfs = []

        # Iterate through files in the directory
        for file in os.listdir(directory):
            # Check if the file is a CSV file
            if file.endswith('.csv'):
                # Process the CSV file and append the DataFrame to the list
                file_path = os.path.join(directory, file)
                df = process_csv(file_path)
                dfs.append(df)

        # Concatenate all DataFrames into a single DataFrame
        final_df = pd.concat(dfs, ignore_index=True)

        # Display markdown for the Sold Homes tab
        st.markdown("# List of Sold Homes")
        # Default columns to display
        default_columns = ['tile', 'href','property_type', 'Bedrooms', 'Bathrooms', 'price', 'Floor Area', 'Province', 'City', 'Suburb', 'Area', "Price per sqm"]

        # Sidebar for selecting columns
        st.sidebar.title("Column Selection")

        # Filter out default columns that don't exist in the dataframe
        default_columns = [col for col in default_columns if col in final_df.columns]

        selected_columns = st.sidebar.multiselect("Select Columns", final_df.columns.tolist(), default=default_columns)
        # Display the DataFrame
        st.write(final_df[selected_columns])
 
    with tab3:
        
        col1, col2 = st.columns(2)

        file_path = "https://raw.githubusercontent.com/Nikhil-Lakha/HouseFlipping/master/Property%20Market%2030%20days.csv"
        df = pd.read_csv(file_path)


        with col1:
            st.write(df)

        df = df[df['Inventory'] <= 6.5]
        # Sort the DataFrame by 'Sold Properties' column in descending order
        df = df.sort_values(by='Inventory', ascending=True)

# Plotting the bar chart using Plotly Express
        fig = px.bar(df, x='Area', y=['Inventory', 'Listed'], barmode='group',
                    labels={'value': 'Number of Properties', 'variable': 'Property Type'},
                    title='Number of Sold Properties vs Listed Properties by Area',
                    height=500)

        # Show plot
        with col2:
            st.plotly_chart(fig)


if __name__ == "__main__":
    main()
